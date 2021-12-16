from abc import abstractmethod

class Packet:
    @staticmethod
    def fromBytes(self, data):
        # TODO
        raise NotImplementedError()

    @abstractmethod
    def toBytes(self, data):
        raise NotImplementedError()


class ExamplePacket(Packet):
    def toBytes(self, data):
        origin = b'example'
        origin = (0).to_bytes(length=1, byteorder="big")  + origin
        return origin