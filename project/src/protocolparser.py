import json

from src.abstractpacket import AbstractPacket
from src.packets import PingPacket, OkPacket, DataTransferPacket, AnonNodeListRequestPacket, \
    AnonNodeListResponsePacket, ErrorPacket, RegisterNodePacket, UnregisterNodePacket


class PacketParser:
    SUPPORTED_PACKETS = [
        PingPacket, OkPacket, ErrorPacket, UnregisterNodePacket, RegisterNodePacket, DataTransferPacket,
        AnonNodeListRequestPacket, AnonNodeListResponsePacket,
    ]
    PACKET_MAP: list[AbstractPacket] = {packet_class.TYPE: packet_class for packet_class in SUPPORTED_PACKETS}
    SEPARATOR = ';'

    def serialize(self, packet: AbstractPacket) -> bytes:
        d = packet.dict()
        s = json.dumps(d)
        return s.encode("utf-8")

    def deserialize(self, buffer) -> AbstractPacket:
        if isinstance(buffer, bytes):
            s = buffer.decode("utf-8")
        else:
            s = buffer
        if len(s) == 0:
            raise Exception("Packet is empty")
        try:
            raw_packet = json.loads(s)
        except json.JSONDecodeError as e:
            raise Exception(f"Json decode error: {e}\nPacket contents:\n{s}")
        packet_class = self.PACKET_MAP[raw_packet["type"]]
        raw_packet.pop("type")
        packet = packet_class(**raw_packet)
        return packet
