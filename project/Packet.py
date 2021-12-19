from abc import abstractmethod


class Packet:

    @staticmethod
    def fromBytes(self, data):
        # TODO
        raise NotImplementedError()

    @staticmethod
    def getType(data):
        return int.from_bytes(data[0:1], byteorder="big")

    @abstractmethod
    def toBytes(self, data):
        raise NotImplementedError()


class ExamplePacket(Packet):
    def toBytes(self, data):
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
    def __init__(self):
        pass

    def fromBytes(self, data):
        pass

    def toBytes(self, data):
        pass



if __name__ == '__main__':
    trp = TrackerReqPacket(1, "31233333")
    temp = trp.toBytes()
    print(trp.toBytes())
    recover = TrackerReqPacket.fromBytes(temp)
