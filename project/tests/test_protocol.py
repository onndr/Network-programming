from src.protocolparser import *
from src.packets import OkPacket
from src.anonnode import AnonNode
import pytest


def test_protocol():
    parser = PacketParser()
    packets_to_test = [
        PingPacket(),
        OkPacket(),
        ErrorPacket("example"),
        UnregisterNodePacket("ip", 69, 69),
        RegisterNodePacket("ip", 100, 100),
        DataTransferPacket("ip", 6969, 100000),
        AnonNodeListRequestPacket(),
        AnonNodeListResponsePacket([
            AnonNode("ip", 69, 70),
            AnonNode("ip2", 1412, 73213),
            AnonNode("ip3", 33, 70),
        ])
    ]

    for packet in packets_to_test:
        buffer = parser.serialize(packet)
        same_packet = parser.deserialize(buffer)
        assert same_packet == packet


def test_empty_list():
    node_list = []
    packet = AnonNodeListResponsePacket(node_list)
    parser = PacketParser()
    serialized = parser.serialize(packet)
    assert packet == parser.deserialize(serialized)


def test_malformed_packets():
    raw = b""
    parser = PacketParser()
    with pytest.raises(Exception):
        packet = parser.deserialize(raw)

    raw = b"{dwiajdowjiwad"
    with pytest.raises(Exception):
        packet = parser.deserialize(raw)
