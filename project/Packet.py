from abc import abstractmethod


class Packet:

    @staticmethod
    def fromBytes(data):
        raise NotImplementedError()

    @staticmethod
    def getType(data):
        return int.from_bytes(data[0:1], byteorder="big")

    @abstractmethod
    def toBytes(self):
        raise NotImplementedError()


class ExamplePacket(Packet):
    def toBytes(self):
        origin = b'example'
        origin = (0).to_bytes(length=1, byteorder="big") + origin
        return origin


class TrackerReqPacket(Packet):
    def __init__(self, op, fid):
        """
        Client向Tracker发包
        :param op: 1：注册，2：下载，3：取消，4：关闭
        :param fid:
        """
        self.op = op
        self.fid = fid

    @staticmethod
    def newRegister(fid):
        return TrackerReqPacket(1, fid)

    @staticmethod
    def newDownload(fid):
        return TrackerReqPacket(2, fid)

    @staticmethod
    def newCancel(fid):
        return TrackerReqPacket(3, fid)

    @staticmethod
    def newClose():
        return TrackerReqPacket(4, "")

    @staticmethod
    def fromBytes(data):
        op = int.from_bytes(data[1:2], byteorder="big")
        fid = data[2:].decode()
        return TrackerReqPacket(op, fid)

    def toBytes(self):
        type = 1
        bts = type.to_bytes(length=1, byteorder="big") + \
              self.op.to_bytes(length=1, byteorder="big") + \
              self.fid.encode()
        return bts

    def __str__(self):
        return "Type:{},op:{},fid:{}".format(1, self.op, self.fid)


class TrackerRespPacket(Packet):
    def __init__(self, info={}):
        self.info = info

    @staticmethod
    def fromBytes(data):
        info = eval(data[1:].decode())
        return TrackerRespPacket(info)

    def toBytes(self):
        type = 2
        bts = type.to_bytes(length=1, byteorder="big") + \
              str(self.info).encode()
        return bts

    def __str__(self):
        return "Type:{},info:{}".format(2, self.info)


class ClientReqPacket(Packet):
    def __init__(self, fid, index):
        self.fid = fid
        self.index = index

    @staticmethod
    def fromBytes(data):
        fid = data[1:37].decode()
        index = int.from_bytes(data[37:], byteorder="big")
        return ClientReqPacket(fid, index)

    def toBytes(self):
        type = 3
        bts = type.to_bytes(length=1, byteorder="big") + \
              self.fid.encode() + \
              self.index.to_bytes(length=4, byteorder="big")
        return bts


class ClientRespPacket(Packet):
    def __init__(self, haveFilePieces, index, data):
        self.haveFilePieces = haveFilePieces
        self.headLength = len(haveFilePieces)
        self.index = index
        self.data = data
        pass

    @staticmethod
    def BoolList2Bytes(boolList: list[bool], length: int):
        num = 1
        for ele in boolList:
            if ele:
                num = (num << 1) + 1
            else:
                num = num << 1
        return num.to_bytes(length=length // 8 + 1, byteorder='big')

    @staticmethod
    def Bytes2BoolList(bbytes: bytes):
        num = int.from_bytes(bbytes, byteorder="big")
        boolList = []
        while num != 1:
            boolList.insert(0, bool(num % 2))
            num //= 2
        return boolList

    @staticmethod
    def fromBytes(data):
        headLength = int.from_bytes(data[1:5], byteorder="big")
        index = int.from_bytes(data[5:9], byteorder="big")
        haveFilePieces = ClientRespPacket.Bytes2BoolList(data[9:9 + headLength // 8 + 1])
        ddata = data[9 + headLength // 8 + 1:]
        return ClientRespPacket(haveFilePieces, index, ddata)

    def toBytes(self):
        type = 4
        bts = type.to_bytes(length=1, byteorder="big") + \
              self.headLength.to_bytes(length=4, byteorder="big") + \
              self.index.to_bytes(length=4, byteorder="big") + \
              ClientRespPacket.BoolList2Bytes(self.haveFilePieces, self.headLength) + \
              self.data
        return bts


if __name__ == '__main__':
    pass
