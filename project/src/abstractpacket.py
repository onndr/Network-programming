class AbstractPacket:
    TYPE = None

    def __init__(self, **kwargs):
        pass

    def dict(self):
        raise NotImplementedError

    def __eq__(self, other):
        return self.dict() == other.dict()

    def __ne__(self, other):
        return not (self == other)
