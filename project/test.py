import json
from FileStorage import FileStorage
from Packet import ClientRespPacket

if __name__ == '__main__':
    # f = FileStorage.fromPath('../test_files/alice.txt')
    # f2 = FileStorage.fromFid(f.fid)
    # f2.add(0, ClientRespPacket(f.fid, [True, True], 0, f.filePieces[0]).data)
    # f2.add(1, ClientRespPacket(f.fid, [True, True], 1, f.filePieces[1]).data)
    # print(f2.isComplete())

    # s = set()
    # s.add("00000001")
    # s.add("2")
    # temp  =str(s).encode().decode()
    # temp1 = eval(temp)
    # print(type(temp1))
    # print(temp1)
    # print(bytes(s))
    # print(set(bytes(s)))

    print(int("00000001"))

