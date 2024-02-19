from src.abstractpacket import AbstractPacket
from src.packets import *


class PacketHandler:
    def __init__(self):
        self.handlers = {}

    def handle(self, packet: AbstractPacket):
        if packet.TYPE in self.handlers:
            return self.handlers[packet.TYPE](packet)
        else:
            raise Exception(f"Unhandled packet type {packet.TYPE}")


class ExampleHandler(PacketHandler):
    def __init__(self):
        super().__init__()
        self.handlers = {
            PingPacket.TYPE: self.handle_ping
        }

    def handle_ping(self, packet: PingPacket):
        print("Recieved ping packet!")
