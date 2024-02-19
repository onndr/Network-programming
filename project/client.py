import socket
import ssl
import sys
import random
from src.protocolparser import PacketParser

from src.packets import AnonNodeListRequestPacket, AnonNodeListResponsePacket, DataTransferPacket

DEFAULTS = [
    "127.0.0.1",
    36969,
    "127.0.0.1",
    8000,
    1000
]

def main():
    if len(sys.argv) < 6:
        print("no args, using defaults")
        print("USAGE:")
        print("central node address: defaults to", DEFAULTS[0])
        print("central node port: defaults to", DEFAULTS[1])
        print("target address: defaults to", DEFAULTS[2])
        print("target port: defaults to", DEFAULTS[3])
        print("amount of data: defaults to", DEFAULTS[4])

        cn_host, cn_port, target_host, target_port, data_amount = DEFAULTS
    else:
        cn_host, cn_port, target_host, target_port, data_amount = (
            str(sys.argv[1]),
            int(sys.argv[2]),
            str(sys.argv[3]),
            int(sys.argv[4]),
            int(sys.argv[5]))

    print("Will connect to central node ", cn_host, ":", cn_port)

    packet_parser = PacketParser()
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        with context.wrap_socket(s, server_hostname="localhost") as ssock:
            ssock.connect((cn_host, cn_port))
            anon_list_request_packet = AnonNodeListRequestPacket()
            buffer = packet_parser.serialize(anon_list_request_packet)
            ssock.sendall(buffer)
            data = ssock.recv(1024)
            anon_list = packet_parser.deserialize(data)
            if not anon_list or (len(anon_list.nodes) == 1 and anon_list.nodes[0].dict()["ip"] == cn_host): # @TODO CHECK if you're the node
                print("Failed to get anon node list, or list is empty")
                return

    data = "Super secret data i want to send"
    data = data * (data_amount // len(data)) + data[:data_amount % len(data)]

    print("Will send data to target node ", target_host, ":", target_port)
    dest_head = DataTransferPacket(target_host, target_port, data_amount)
    data = "Super secret data i want to send"
    data = data * (data_amount // len(data)) + data[:data_amount % len(data)]

    random_node_dict = random.choice(anon_list.nodes).dict()
    while True:
        try:
            with socket.create_connection((random_node_dict["ip"], random_node_dict["data_port"])) as sock:
                sock.settimeout(5)
                with context.wrap_socket(sock, server_hostname="localhost") as ssock:
                    head_buffer = packet_parser.serialize(dest_head)
                    ssock.sendall(head_buffer)
                    ssock.sendall(packet_parser.SEPARATOR.encode("utf-8"))
                    ssock.sendall(data.encode("utf-8"))
                    print("Success")
                    break
        except:
            print("Failed to connect to target node")
            print(random_node_dict["ip"], ":", random_node_dict["data_port"])


if __name__ == "__main__":
    main()
