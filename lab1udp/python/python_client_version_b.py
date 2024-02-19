"""
    Kod rozwinięty przez: Andrii Gamalii oraz Wiktor Topolski
"""

import socket
import argparse
import time
from python_protocol import generate_wrong_packet


def main():
    parser = argparse.ArgumentParser(description='Client in python')
    parser.add_argument('host', help='server ip address', type=str)
    parser.add_argument('port', help='server port', type=int)
    parser.add_argument('start_size', help='size of first datagram sent in BYTES', type=int)
    parser.add_argument('end_size', help='size of last datagram in BYTES', type=int)
    parser.add_argument('count', help='number of packets to send', type=int)
    parser.add_argument('delay_in_ms', help='delay between packets', type=int)
    args = parser.parse_args()

    HOST = args.host
    PORT = args.port
    START_SIZE = args.start_size
    END_SIZE = args.end_size
    PACKETS_COUNT = args.count
    PACKETS_DELAY = args.delay_in_ms / 1000

    size = 100000

    if PACKETS_COUNT == 1:
        packet_sizes = [END_SIZE]
    else:
        packet_sizes = [START_SIZE]
        for i in range(PACKETS_COUNT - 1):
            packet_sizes.append(packet_sizes[i] + (END_SIZE - START_SIZE) // (PACKETS_COUNT - 1))

    print("Will send to ", HOST, ":", PORT)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        for i in range(PACKETS_COUNT):
            packet_size = packet_sizes[i]
            print(f'Sending packet {i+1}, datagram size: {packet_size}')
            try:
                s.sendto(generate_wrong_packet(packet_size), (HOST, PORT))
            except Exception as e:
                print("Error sending packet: ", str(e))
            data = s.recv(size)
            print('Received from server',  data[8:].decode('ascii'))
            time.sleep(PACKETS_DELAY)


main()
