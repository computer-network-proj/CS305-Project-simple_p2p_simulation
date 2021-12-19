from abc import abstractmethod
from enum import Enum



class TrackerOperation(Enum):
    REGISTER = 1
    DOWNLOAD = 2
    CANCEL = 3
    CLOSE = 4


def case1():
    return b'0001'


def case2():
    return b'0010'


def case3():
    return b'0011'


def case4():
    return b'0100'


def default():
    raise NotImplementedError()


switch = {TrackerOperation.REGISTER: case1,
          TrackerOperation.DOWNLOAD: case2,
          TrackerOperation.CANCEL: case3,
          TrackerOperation.CLOSE: case4}


switchOperation = {
    b'0001': lambda :TrackerOperation.REGISTER,
    b'0010': lambda :TrackerOperation.DOWNLOAD,
    b'0011': lambda :TrackerOperation.CANCEL,
    b'0100': lambda :TrackerOperation.CLOSE
}

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


class TrackerPacket(Packet):
    @staticmethod
    def generatePacket(type,data):
        header = b'0'
        typeByte = switch.get(type, default)()
        return header + typeByte + data

    @staticmethod
    def generateInformation(data):
        header = data[0:1]
        type = switchOperation.get(data[1:5],default)()
        info = data[5:]
        return header,type,info

class TrackerReqPacket(Packet):
    def __init__(self, op, fid):
        """
        Client向Tracker发包
        :param op: 1：注册，2：下载，3：取消，4：关闭
        :param fid:
        """
        self.op = op
        self.fid = fid

    @classmethod
    def fromBytes(cls, data):
        op = int(data[9:16])

    def toBytes(self):
        type = 1
        bts = type.to_bytes(length=1, byteorder="big") + \
                self.op.to_bytes(length=1, byteorder="big") + \
                self.fid.encode()
        return bts

