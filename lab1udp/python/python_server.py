"""
    (c) G.Blinowski for PSI 2021
    Kod rozwinięty przez: Andrii Gamalii oraz Wiktor Topolski
"""

import argparse
import socket
from python_protocol import verify_packet, generate_response_packet


def main():
    parser = argparse.ArgumentParser(description='Server in python')
    parser.add_argument('port', help='server port', type=int)
    # parser.add_argument('ip', help="sever ip", type=str)
    args = parser.parse_args()

    HOST = socket.gethostname()
    PORT = args.port
    BUFSIZE = 100000

    print("Will listen on ", HOST, ":", PORT)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        i = 1
        while True:
            try:
                data_address = s.recvfrom(BUFSIZE)
            except Exception as e:
                print("Error receiving data: ", str(e))

            data = data_address[0]
            address = data_address[1]

            print(f"Received {len(data)} bytes from {address[0]}:{address[1]}")

            if not data:
                print("Error in datagram?")
                continue

            status, length, seq_num = verify_packet(data)
            if status:
                response = generate_response_packet(length, "OK", seq_num)
                print("Packet check 1")
            else:
                response = generate_response_packet(length, "ERROR", seq_num)
                print("Packet check 0")
            print(f'recvfrom ok')

            try:
                s.sendto(response, address)
            except Exception as e:
                print("Error sending data: ", str(e))

            i += 1


main()
