from abc import abstractmethod


class Packet:

    @staticmethod
    def fromBytes(data):
        raise NotImplementedError()

    @staticmethod
    def getType(data):
        return int.from_bytes(data[0:1], byteorder="big")

    @staticmethod
    def getFid(data):
        return data[1:37]

    @abstractmethod
    def toBytes(self):
        raise NotImplementedError()


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
        return TrackerReqPacket(4, b"0"*36)

    @staticmethod
    def fromBytes(data):
        fid = Packet.getFid(data)
        op = int.from_bytes(data[37:38], byteorder="big")

        return TrackerReqPacket(op, fid)

    def toBytes(self):
        type = 1
        bts = type.to_bytes(length=1, byteorder="big") + \
              self.fid + \
              self.op.to_bytes(length=1, byteorder="big")
        return bts

    def __str__(self):
        return "Type:{},op:{},fid:{}".format(1, self.op, self.fid)


class TrackerRespPacket(Packet):
    def __init__(self, fid, info={}):
        self.fid = fid
        self.info = info

    @staticmethod
    def fromBytes(data):
        fid = Packet.getFid(data)
        tmp = data[37:].decode()
        info = eval(data[37:].decode())
        return TrackerRespPacket(fid, info)

    def toBytes(self):
        type = 2
        bts = type.to_bytes(length=1, byteorder="big") + \
              self.fid + \
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
        fid = Packet.getFid(data)
        index = int.from_bytes(data[37:], byteorder="big") - 100
        return ClientReqPacket(fid, index)

    def toBytes(self):
        type = 3
        bts = type.to_bytes(length=1, byteorder="big") + \
              self.fid + \
              (self.index + 100).to_bytes(length=4, byteorder="big")
        return bts


class ClientRespPacket(Packet):
    def __init__(self, fid, haveFilePieces, index, data):
        self.fid = fid
        self.haveFilePieces = haveFilePieces
        self.headLength = len(haveFilePieces)
        self.index = index
        self.data = data

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
        fid = Packet.getFid(data)
        headLength = int.from_bytes(data[37:41], byteorder="big")
        index = int.from_bytes(data[41:45], byteorder="big") - 100
        haveFilePieces = ClientRespPacket.Bytes2BoolList(data[45:45 + headLength // 8 + 1])
        ddata = data[45 + headLength // 8 + 1:]
        return ClientRespPacket(fid, haveFilePieces, index, ddata)

    def toBytes(self):
        type = 4
        bts = type.to_bytes(length=1, byteorder="big") + \
              self.fid + \
              self.headLength.to_bytes(length=4, byteorder="big") + \
              (self.index + 100).to_bytes(length=4, byteorder="big") + \
              ClientRespPacket.BoolList2Bytes(self.haveFilePieces, self.headLength) + \
              self.data
        return bts


if __name__ == '__main__':
    pass
