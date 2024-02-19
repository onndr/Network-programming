import socket
import ssl
from sys import argv
import logging

KEYFILE = "server.key"
CERTFILE = "server.crt"


def start_tls_server(host: str, port: int, key_file: str, cert_file: str):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    logging.info(f"Reciever listening on port {port}")

    while True:
        client_socket, client_address = server_socket.accept()
        logging.info(f"Accepted connection from {client_address}")

        try:
            ssl_socket = ssl.wrap_socket(client_socket, server_side=True, keyfile=key_file,
                                         certfile=cert_file, ssl_version=ssl.PROTOCOL_TLS)

            while True:
                data = ssl_socket.recv(4096)
                if not data:
                    logging.info(f"Connection closed by {client_address}")
                    break

                decoded = data.decode("utf-8")
                fragment = decoded[0:min(15, len(decoded))]
                logging.info(f"Recived {len(data)} bytes: {fragment}...")
            ssl_socket.close()
        except ssl.SSLError as e:
            logging.info(f"SSL error: {e}")


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d [%(levelname)s] - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    HOST = "localhost"
    PORT = 8000
    if len(argv) == 3:
        HOST = argv[1]
        PORT = int(argv[2])

    start_tls_server(HOST, PORT, KEYFILE, CERTFILE)


if __name__ == "__main__":
    main()
