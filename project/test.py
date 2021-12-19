import json
from FileStorage import FileStorage
from Packet import ClientRespPacket

if __name__ == '__main__':
    f = FileStorage.fromPath('../test_files/alice.txt')
    f2 = FileStorage.fromFid(f.fid)
    f2.add(0,ClientRespPacket([True,True],0,f.filePieces[0]).data)
    f2.add(1,ClientRespPacket([True,True],1,f.filePieces[1]).data)
    print(f2.isComplete())