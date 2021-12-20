import time

from Packet import TrackerReqPacket, Packet, TrackerRespPacket, ClientRespPacket
from PClient import PClient
from DownloadTask import DownloadTask
from FileStorage import FileStorage
import threading

from Proxy import Proxy


class ProjectPClient(PClient):

    def __init__(self, tracker_addr: (str, int), proxy=None, port=None, upload_rate=0, download_rate=0):
        super().__init__(tracker_addr, proxy, port, upload_rate, download_rate)
        self.active = True

        self.tasks = {}
        # self.fidMap = {}

        threading.Thread(target=self.recvThread).start()
        # TODO our init code

    def recvThread(self):
        while self.active:
            packet, cid = self.__recv__()
            packetType = Packet.getType(packet)



            fid = Packet.getFid(packet)
            if fid in self.tasks.keys():
                self.tasks[fid].pipe.recv_queue.put((packet,cid))
                if packetType == 4:
                    pass
                    # self.tasks[fid].fileStorage.display()
                    # pieces = self.tasks[fid].fileStorage.haveFilePieces
                    # print(str(cid[1]) + ' > ' + str(self.proxy.port) + " " + str(round(sum(pieces) / len(pieces), 5)) + "\n", end="")
                    # # print(self.tasks[fid].fileStorage.display())
            else:
                print("miss")



    def register(self, file_path: str):
        fileStorage = FileStorage.fromPath(file_path)
        # packet = TrackerPacket.generatePacket(TrackerOperation.REGISTER,byteFid)
        fid = fileStorage.fid
        if fid in self.tasks:
            self.tasks[fid].fileStorage = fileStorage
        else:
            new_task = DownloadTask(fileStorage, self.__send__, selfPort=self.proxy.port)
            self.tasks[fid] = new_task

        packet = TrackerReqPacket.newRegister(fileStorage.fid)
        packet = packet.toBytes()
        self.__send__(packet, self.tracker)
        return fid

        # TODO our code

    def download(self, fid) -> bytes:
        # TODO 这里需要上线程锁
        # if task already exists:

        if fid in self.tasks:
            return self.tasks[fid].get_file()

        new_task = DownloadTask(FileStorage.fromFid(fid), self.__send__, selfPort=self.proxy.port)
        self.tasks[fid] = new_task

        packet = TrackerReqPacket.newDownload(fid)
        packet = packet.toBytes()
        self.__send__(packet, self.tracker)

        return new_task.getFile()

    def cancel(self, fid):
        # packet = TrackerPacket.generatePacket(TrackerOperation.CANCEL,fid.encode())
        packet = TrackerReqPacket.newCancel(fid)
        packet = packet.toBytes()
        self.__send__(packet, self.tracker)

        tmp = self.tasks.pop(fid)
        tmp.close()
        # TODO our code

    def close(self):
        packet = TrackerReqPacket.newClose()
        packet = packet.toBytes()
        self.__send__(packet, self.tracker)

        temp = self.tasks
        self.tasks ={}
        for key in temp.keys():
            temp[key].close()
        # TODO our code


if __name__ == '__main__':
    tracker_address = ("127.0.0.1", 10086)
    # file_path = '../test_files/alice.txt'
    file_path = '../test_files/bg.png'
    PC1 = ProjectPClient(tracker_address, upload_rate=100000, download_rate=100000)
    PC2 = ProjectPClient(tracker_address, upload_rate=100000, download_rate=100000)
    PC3 = ProjectPClient(tracker_address, upload_rate=100000, download_rate=100000)
    PC1.register(file_path)
    PC2.register(file_path)
    PC3.register(file_path)
    fid = FileStorage.fromPath(file_path).fid
    print(fid)
    time.sleep(1)
    PC1.close()

    PC1.cancel(fid)
    PC1.cancel(fid)
    PC2.cancel(fid)
    PC1.close()
    PC2.close()
    PC3.close()
