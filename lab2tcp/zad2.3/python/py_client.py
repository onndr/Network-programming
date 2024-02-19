import socket
import sys
from datastruct import ListNode, DataList
from protocol import DataListProtocol


def prepare_data(n_of_elements: int, content_size: int) -> DataList:
    data = DataList()
    for i in range(n_of_elements):
        data.add_node(ListNode(
            i, i * 2, i * 3, f"Book by {i}", "a" * content_size)
        )
    return data


DEFAULTS = [
    "v4",
    "127.0.0.1",
    8888,
    10,
    1000
]

def main():
    if len(sys.argv) < 6:
        print("no args, using defaults")
        print("USAGE:")
        print("ip protocol: v4 or v6 defaults to", DEFAULTS[0])
        print("adress: defaults to", DEFAULTS[1])
        print("port: defaults to", DEFAULTS[2])
        print("node_count: defaults to", DEFAULTS[3])
        print("content_size: defaults to", DEFAULTS[4])

        ip, host, port, node_count, content_size = DEFAULTS
    else:
        ip, host, port, node_count, content_size = (
            str(sys.argv[1]),
            str(sys.argv[2]),
            int(sys.argv[3]),
            int(sys.argv[4]),
            int(sys.argv[5]))

    print("Will connect to ", host, ":", port)

    initial_data = prepare_data(node_count, content_size)
    buffer = DataListProtocol.serialize_packet(initial_data)

    print("Sending", len(buffer), "bytes!")

    if ip == "v4":
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(buffer)
    elif ip == "v6":
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
            s.connect((host, port, 0, 0))
            s.sendall(buffer)
    print("Data sent")


if __name__ == "__main__":
    main()
