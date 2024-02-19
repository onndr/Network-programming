from src.abstractpacket import AbstractPacket
from src.anonnode import AnonNode


class PingPacket(AbstractPacket):
    """
    Respond to the ping with a OkPacket - pong packet has been removed
    """
    TYPE = 'PING'

    def dict(self):
        return {"type": self.TYPE}


class OkPacket(AbstractPacket):
    TYPE = 'OK'
    pass

    def dict(self):
        return {"type": self.TYPE}


class ErrorPacket(AbstractPacket):
    TYPE = 'ERROR'
    pass

    def __init__(self, content: str):
        super().__init__()
        self.content = content

    def dict(self):
        return {
            "type": self.TYPE,
            "content": self.content
        }


class DataTransferPacket(AbstractPacket):
    TYPE = 'DATA'

    def __init__(self, recipient_ip: str, recipient_port: int, total_size: int):
        super().__init__()
        self.recipient_ip = recipient_ip
        self.recipient_port = recipient_port
        self.total_size = total_size

    def dict(self):
        return {
            "type": self.TYPE,
            "recipient_ip": self.recipient_ip,
            "recipient_port": self.recipient_port,
            "total_size": self.total_size
        }


class AnonNodeListRequestPacket(AbstractPacket):
    TYPE = 'GET-NODES'

    def dict(self):
        return {"type": self.TYPE}


class AnonNodeListResponsePacket(AbstractPacket):
    TYPE = 'NODES'

    def __init__(self, nodes):
        """
        :param nodes: can either be a dict representation or a list of anon nodes
        """
        super().__init__()
        if len(nodes) == 0:
            self.nodes = []
        elif isinstance(nodes[0], dict):
            self.nodes = [AnonNode(**node_args) for node_args in nodes]
        elif isinstance(nodes[0], AnonNode):
            self.nodes = nodes

    def dict(self):
        return {
            "type": self.TYPE,
            "nodes": [node.dict() for node in self.nodes]
        }


class RegisterNodePacket(AbstractPacket):
    TYPE = "REGISTER"

    def __init__(self, ip: str, status_port: int, data_port: int):
        super().__init__()
        self.node = AnonNode(ip, status_port, data_port)

    def dict(self):
        return {
            "type": self.TYPE,
            **self.node.dict()
        }


class UnregisterNodePacket(AbstractPacket):
    TYPE = "UNREGISTER"

    def __init__(self, ip: str, status_port: int, data_port: int):
        super().__init__()
        self.node = AnonNode(ip, status_port, data_port)

    def dict(self):
        return {
            "type": self.TYPE,
            **self.node.dict()
        }
