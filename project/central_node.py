import argparse
import socket
import ssl
import sys
import threading
import time

from src.anonnode import AnonNode
from src.packets import PingPacket, OkPacket, AnonNodeListRequestPacket, RegisterNodePacket, UnregisterNodePacket, \
    AnonNodeListResponsePacket, ErrorPacket
from src.protocolparser import PacketParser


class NodeListEntry:
    def __init__(self, node: AnonNode, failed_requests: int = 0):
        self._node = node
        self._failed_requests = failed_requests

    def request_failed(self):
        print(f"Failed to ping {self._node.ip}:{self._node.status_port}, failure {self._failed_requests}")
        self._failed_requests += 1

    def failed_requests(self):
        return self._failed_requests

    def node(self):
        return self._node


class CentralNode(AnonNode):
    def __init__(self, ip: str, port: int, keyfile: str, certfile: str):
        super().__init__(ip, port, 0)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._keyfile = keyfile
        self._certfile = certfile
        self._packet_parser = PacketParser()
        self._nodes: list[NodeListEntry] = []
        self._work = True

    def _get_nodes_list(self):
        """
        Returns a list of nodes and their data to respond to an AnonNodeRequestPacket
        """
        nodes_list = []
        for node_entry in self._nodes:
            nodes_list.append(AnonNode(node_entry.node().ip, node_entry.node().status_port, node_entry.node().data_port))
        return nodes_list

    def _add_node_to_list(self, new_node: AnonNode) -> bool:
        """
        Adds a node to the list if it's not on the list yet
        """
        for node_entry in self._nodes:
            if node_entry.node().ip == new_node.ip and node_entry.node().status_port == new_node.status_port and node_entry.node().data_port == new_node.data_port:
                return False
        self._nodes.append(NodeListEntry(new_node))
        return True

    def _remove_node_from_list(self, node_to_remove: AnonNode) -> bool:
        """
        Removes a node from the list if it's listed
        """
        to_remove = None
        for node_entry in self._nodes:
            if node_entry.node().ip == node_to_remove.ip and node_entry.node().status_port == node_to_remove.status_port and node_entry.node().data_port == node_to_remove.data_port:
                to_remove = node_entry
                break
        if to_remove is not None:
            self._nodes.remove(to_remove)
            return True
        return False

    def _ping_thread(self):
        """
        Ping all nodes every minute, remove them from the list of nodes after 3 failed replies
        """
        while self._work:
            start_time = time.time()
            for node_entry in self._nodes:
                # Send a ping to a node
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(5)
                    try:
                        encrypted_socket = ssl.wrap_socket(sock, keyfile=self._keyfile,
                                                           certfile=self._certfile, ssl_version=ssl.PROTOCOL_TLS)
                        encrypted_socket.connect((node_entry.node().ip, node_entry.node().status_port))
                        ping_packet = PingPacket()
                        encrypted_socket.sendall(self._packet_parser.serialize(ping_packet))
                        # wait for the confirmation
                        confirmation = encrypted_socket.recv(1024)
                        packet = self._packet_parser.deserialize(confirmation)
                        if packet.TYPE != OkPacket.TYPE:
                            node_entry.request_failed()
                        else:
                            print(
                                f"Successfully pinged {node_entry.node().ip}:{node_entry.node().status_port}, data port {node_entry.node().data_port}")
                        sock.close()
                    except ssl.SSLError:
                        node_entry.request_failed()
                    except TimeoutError:
                        node_entry.request_failed()
                    except ConnectionRefusedError:
                        node_entry.request_failed()
            # remove nodes that timed out 3 times
            to_remove = []
            for node_entry in self._nodes:
                if node_entry.failed_requests() >= 3:
                    to_remove.append(node_entry)
            for node_entry in to_remove:
                self._nodes.remove(node_entry)
            # wait for the next loop (in case it hasn't been a minute already)
            processing_time = time.time() - start_time
            if processing_time < 60:
                time.sleep(60 - processing_time)

    def _list_thread(self):
        """
        Listen for incoming connections of nodes registering, unregistering or requesting the nodes list
        """
        self._socket.bind((self.ip, self.status_port))
        self._socket.listen(5)
        print(f"Central node listening on {self.ip}:{self.status_port}")

        while self._work:
            client_socket, client_address = self._socket.accept()
            try:
                encrypted_socket = ssl.wrap_socket(client_socket, server_side=True, keyfile=self._keyfile,
                                                   certfile=self._certfile, ssl_version=ssl.PROTOCOL_TLS)
                data = encrypted_socket.recv(1024)
                packet = self._packet_parser.deserialize(data)
                if packet.TYPE == AnonNodeListRequestPacket.TYPE:
                    nodes_list = self._get_nodes_list()
                    response_packet = AnonNodeListResponsePacket(nodes_list)
                    response_bytes = self._packet_parser.serialize(response_packet)
                    encrypted_socket.sendall(response_bytes)
                    print(f"Sent nodes list to {client_address}")
                elif packet.TYPE == RegisterNodePacket.TYPE:
                    request_packet = self._packet_parser.deserialize(data)
                    new_node = request_packet.node
                    response_packet = OkPacket()
                    if not self._add_node_to_list(new_node):
                        response_packet = ErrorPacket("Node already registered")
                        print(f"Registration of node {new_node.ip}:{new_node.status_port} rejected: node already "
                              f"registered")
                    response_bytes = self._packet_parser.serialize(response_packet)
                    encrypted_socket.sendall(response_bytes)
                    print(f"Node {new_node.ip}:{new_node.status_port}, data port {new_node.data_port} registered")
                elif packet.TYPE == UnregisterNodePacket.TYPE:
                    request_packet = self._packet_parser.deserialize(data)
                    node_to_remove = request_packet.node
                    response_packet = OkPacket()
                    if not self._remove_node_from_list(node_to_remove):
                        response_packet = ErrorPacket("Node not registered")
                        print(
                            f"Delisting of node {node_to_remove.ip}:{node_to_remove.status_port} rejected: node not registered")
                    response_bytes = self._packet_parser.serialize(response_packet)
                    encrypted_socket.sendall(response_bytes)
                    print(
                        f"Node {node_to_remove.ip}:{node_to_remove.status_port}, data port {node_to_remove.data_port} delisted")
                else:
                    print(f"Received a packet of type {packet.TYPE} that shouldn't be here")
                encrypted_socket.close()
            except ssl.SSLError as e:
                print(f"SSL Error: {e}")

    def start(self):
        ping_thread = threading.Thread(target=self._ping_thread)
        list_thread = threading.Thread(target=self._list_thread)
        ping_thread.start()
        list_thread.start()

    def stop(self):
        self._work = False


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=36969)
    parser.add_argument("--keyfile", type=str, default="server.key")
    parser.add_argument("--certfile", type=str, default="server.crt")
    args = parser.parse_args(argv[1:])

    central_node = CentralNode(args.ip, args.port, args.keyfile, args.certfile)
    central_node.start()


if __name__ == "__main__":
    main(sys.argv)
