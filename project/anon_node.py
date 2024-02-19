import argparse
import enum
import random
import socket
import ssl
import threading
import time
from src.abstractpacket import AbstractPacket

from src.anonnode import AnonNode
from src.protocolparser import PacketParser
from src.packethandling import PacketHandler
from src.packets import PingPacket, RegisterNodePacket, UnregisterNodePacket, DataTransferPacket, OkPacket, ErrorPacket


class Session:
    def __init__(self, client_ip, client_port, dest_ip, dest_port):
        self.client = (client_ip, client_port)
        self.dest = (dest_ip, dest_port)
        self.client_socket = None
        self.dest_socket = None


class INodeState(enum.Enum):
    INITIALIZED = 0
    REGISTERED = 1
    LISTENING = 2


class IntermediateNode(AnonNode):
    def __init__(self, ip: str, status_port: int, data_port: int,
                 central_node_ip: str, central_node_port: int,
                 certfile: str, keyfile: str):
        super().__init__(ip, status_port, data_port)
        self.central_node = (central_node_ip, central_node_port)
        self.sessions = []
        self.packet_parser = PacketParser()
        self.status_socket = None
        self.data_socket = None
        self.BUF_SIZE = 32768
        self.state = INodeState.INITIALIZED
        self.certfile = certfile
        self.keyfile = keyfile
        self.packet_handler = PacketHandler()

    def register(self):
        # create a client status socket
        self.status_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.status_socket = ssl.wrap_socket(self.status_socket, certfile=self.certfile, keyfile=self.keyfile)
            self.status_socket.connect(self.central_node)
            register_packet = RegisterNodePacket(self.ip, self.status_port, self.data_port)
            serialized_register_packet = self.packet_parser.serialize(register_packet)
            self.status_socket.sendall(serialized_register_packet)
        except Exception as e:
            self.status_socket.close()
            print(e)
            exit(1)

        # Wait for OkPacket from central node
        while True:
            data = self.status_socket.recv(self.BUF_SIZE)
            if not data:
                break
            packet = self.packet_parser.deserialize(data)
            if packet.TYPE == OkPacket.TYPE:
                break

        self.state = INodeState.REGISTERED

        # Start a new thread to listen for incoming packets from the central node
        threading.Thread(target=self.listen_for_packets).start()

    def listen_for_packets(self):
        self.status_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.status_socket = ssl.wrap_socket(self.status_socket, certfile=self.certfile, keyfile=self.keyfile)
        self.status_socket.bind((self.ip, self.status_port))
        self.status_socket.listen()
        while True:
            new_socket, address = self.status_socket.accept()
            data = new_socket.recv(self.BUF_SIZE)
            if not data:
                break
            packet = self.packet_parser.deserialize(data)
            self.handle_packet(packet, reply_socket=new_socket)

    def unregister(self):
        unregister_packet = UnregisterNodePacket(self.ip, self.status_port, self.data_port)
        serialized_unregister_packet = self.packet_parser.serialize(unregister_packet)
        self.status_socket.sendall(serialized_unregister_packet)

        # Wait for OkPacket from central node
        while True:
            data = self.status_socket.recv(self.BUF_SIZE)
            if not data:
                break
            packet = self.packet_parser.deserialize(data)
            if packet.TYPE == OkPacket.TYPE:
                break

        # Close all sockets
        self.status_socket.close()
        for session in self.sessions.values():
            session.client_socket.close()
            if session.dest_socket is not None:
                session.dest_socket.close()

    def listen_for_clients(self):
        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_socket.bind((self.ip, self.data_port))
        self.data_socket.listen(5)
        self.state = INodeState.LISTENING

        while True:
            client_socket, client_address = self.data_socket.accept()
            session = Session(client_address[0], client_address[1], None, None)
            self.sessions.append(session)
            threading.Thread(target=self.handle_client, args=(client_socket, session)).start()

    def handle_client(self, client_socket, session, certfile="server.crt", keyfile="server.key"):
        # Wrap the client socket with SSL
        client_socket = ssl.wrap_socket(client_socket, server_side=True, certfile=certfile, keyfile=keyfile)
        buffer = ""
        header_received = False
        total_size = 0
        while True:
            data = client_socket.recv(self.BUF_SIZE)
            if not data:
                break
            data = data.decode("utf-8")

            if not header_received:
                buffer += data
                if ";" in buffer:
                    packet_data, buffer = buffer.split(";", 1)
                    packet = self.packet_parser.deserialize(packet_data)
                    total_size = packet.total_size
                    self.handle_packet(packet, session)
                    header_received = True

            if header_received:
                buffer += data
                if len(buffer) >= total_size:
                    parts = self.split_data_randomly(buffer)
                    for part in parts:
                        time.sleep(random.uniform(0.5, 1.5))  # Random delay before sending data
                        session.dest_socket.send(part.encode("utf-8"))
                    buffer = ""
        client_socket.close()

    def split_data_randomly(self, data):
        parts = []
        while len(data) > 0:
            split_point = random.randint(1,
                                         min(len(data), 1024))  # Randomly split the data, but no more than 1024 bytes
            part = data[:split_point]
            data = data[split_point:]
            parts.append(part)
        return parts

    def handle_packet(self, packet: AbstractPacket, session=None, reply_socket=None):
        if packet.TYPE == DataTransferPacket.TYPE and session is not None:
            session.dest = (packet.recipient_ip, packet.recipient_port)
            session.dest_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            session.dest_socket = ssl.wrap_socket(session.dest_socket, keyfile=self.keyfile,
                                                  certfile=self.certfile, ssl_version=ssl.PROTOCOL_TLS)
            session.dest_socket.connect(session.dest)
        elif packet.TYPE == PingPacket.TYPE:
            ok_packet = OkPacket()
            serialized_ok_packet = self.packet_parser.serialize(ok_packet)
            reply_socket.sendall(serialized_ok_packet)
        elif packet.TYPE == OkPacket.TYPE:
            print("Got OkPacket from central node")
        elif packet.TYPE == ErrorPacket.TYPE:
            if packet.content == "Node already registered":
                print("Node already registered")
            elif packet.content == "Node not registered":
                print("Node not registered")
        else:
            raise ValueError("Unknown packet type")


def main():
    # read central node ip and port from args
    parser = argparse.ArgumentParser()
    parser.add_argument("central_node_ip", type=str)
    parser.add_argument("central_node_port", type=int)
    parser.add_argument("ip", type=str)
    parser.add_argument("status_port", type=int)
    parser.add_argument("data_port", type=int)
    parser.add_argument("certfile", type=str)
    parser.add_argument("keyfile", type=str)
    args = parser.parse_args()
    ip = args.ip
    status_port = args.status_port
    data_port = args.data_port
    central_node_ip = args.central_node_ip
    central_node_port = args.central_node_port
    certfile = args.certfile
    keyfile = args.keyfile

    # create intermediate node
    inode = IntermediateNode(ip, status_port, data_port, central_node_ip, central_node_port, certfile, keyfile)
    inode.register()
    inode.listen_for_clients()


if __name__ == "__main__":
    main()
