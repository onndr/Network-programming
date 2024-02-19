"""
    (c) G.Blinowski for PSI 2021
    Kod rozwinięty przez: Andrii Gamalii oraz Wiktor Topolski
"""

import socket
import argparse
import time
from python_protocol import generate_correct_packet


def main():
    parser = argparse.ArgumentParser(description='Client in python')
    parser.add_argument('host', help='server ip address', type=str)
    parser.add_argument('port', help='server port', type=int)
    parser.add_argument('count', help='number of packets to send', type=int)
    parser.add_argument('delay_in_ms', help='delay between packets', type=int)
    args = parser.parse_args()

    HOST = args.host
    PORT = args.port
    PACKETS_COUNT = args.count
    PACKETS_DELAY = args.delay_in_ms / 1000

    size = 1024

    print("Will send to ", HOST, ":", PORT)
    datagram_length = 50

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        for i in range(PACKETS_COUNT):
            print(f'Sending packet {i+1}')
            try:
                s.sendto(generate_correct_packet(datagram_length, i), (HOST, PORT))
            except Exception as e:
                print("Error sending packet: ", str(e))
            data = s.recv(size)
            recvd_dg_length = int.from_bytes(data[:2], byteorder="little", signed=True)
            recvd_seq_num = int.from_bytes(data[4:8], byteorder="little", signed=True)

            # resend until get the proper response
            while datagram_length != recvd_dg_length and recvd_seq_num != i:
                try:
                    s.sendto(generate_correct_packet(datagram_length, i), (HOST, PORT))
                except Exception as e:
                    print("Error sending packet: ", str(e))
                recvd_dg_length = int.from_bytes(data[:2], byteorder="little", signed=True)
                recvd_seq_num = int.from_bytes(data[4:8], byteorder="little", signed=True)

            print(f'Received from server: [len:{recvd_dg_length}, seq:{recvd_seq_num}] {data[8:].decode("ascii")}')
            time.sleep(PACKETS_DELAY)


main()
