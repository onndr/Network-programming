class AnonNode:
    def __init__(self, ip: str, status_port: int, data_port: int):
        self.ip = ip
        self.status_port = status_port
        self.data_port = data_port

    def dict(self):
        return {
            "ip": self.ip,
            "status_port": self.status_port,
            "data_port": self.data_port
        }
