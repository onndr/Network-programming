"""
    Kod rozwinięty przez: Andrii Gamalii oraz Wiktor Topolski
"""

import io


def verify_packet(data: bytes):
    length = len(data)
    if length < 8:
        return False, 0, -1

    dg_length = int.from_bytes(data[:2], byteorder="little", signed=True)
    seq_num = int.from_bytes(data[4:8], byteorder="little", signed=True)
    if dg_length != length - 8:
        return False, dg_length, 0

    datagram = data[8:].decode('ascii')
    A = ord('A')
    Z = ord('Z')
    for i in range(dg_length):
        code = A + i % (Z - A + 1)
        if code != ord(datagram[i]):
            return False, dg_length, seq_num

    return True, dg_length, seq_num


def generate_response_packet(datagram_len: int, message: str, seq_num: int):
    binary_stream = io.BytesIO()
    binary_stream.write(datagram_len.to_bytes(2, "little", signed=True))
    binary_stream.write(b"00")
    binary_stream.write(seq_num.to_bytes(4, "little", signed=True))
    binary_stream.write(message.encode('ascii'))
    binary_stream.seek(0)
    stream_data = binary_stream.read()
    return stream_data


def generate_correct_packet(datagram_len: int, sequence_num: int):
    binary_stream = io.BytesIO()
    binary_stream.write(datagram_len.to_bytes(2, "little", signed=True))
    binary_stream.write(b"00")
    binary_stream.write(sequence_num.to_bytes(4, "little", signed=True))
    A = ord('A')
    Z = ord('Z')
    for i in range(datagram_len):
        code = A + i % (Z - A + 1)
        binary_stream.write(chr(code).encode('ascii'))
    binary_stream.seek(0)
    stream_data = binary_stream.read()
    return stream_data


def generate_wrong_packet(datagram_len: int = 30):
    binary_stream = io.BytesIO()
    wrong_string = "This packet doesn't make sense"
    for i in range(datagram_len):
        binary_stream.write(wrong_string[i % len(wrong_string)].encode('ascii'))
    binary_stream.seek(0)
    stream_data = binary_stream.read()
    return stream_data
