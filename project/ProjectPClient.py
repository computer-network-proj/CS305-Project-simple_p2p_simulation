import time

from Packet import TrackerReqPacket,Packet,TrackerRespPacket
from PClient import PClient
from DownloadTask import DownloadTask
from FileStorage import FileStorage
import threading


from Proxy import Proxy


class ProjectPClient(PClient):

    def __init__(self, tracker_addr: (str, int), proxy=None, port=None, upload_rate=0, download_rate=0):
        super().__init__(tracker_addr, proxy, port, upload_rate, download_rate)
        self.active =True
        self.tasks = []
        self.fidMap = {}
        threading.Thread(target=self.recvThread).start()
        #TODO our init code


    def recvThread(self):
        while self.active:
            packet, cid = self.__recv__()
            packetType = Packet.getType(packet)
            if packetType == 2:
                pass
            if packetType == 4:
                pass
            print(str(self.proxy.port)+ " " + TrackerRespPacket.fromBytes(packet).__str__()+"\n",end="")

    def register(self, file_path: str):
        fileStorage = FileStorage.fromPath(file_path)
        # packet = TrackerPacket.generatePacket(TrackerOperation.REGISTER,byteFid)
        packet = TrackerReqPacket.newRegister(fileStorage.fid)
        packet = packet.toBytes()
        self.__send__(packet,self.tracker)
        # TODO our code

    def download(self, fid) -> bytes:
        # TODO 这里需要上线程锁
        # if task already exists:
        for task in self.tasks:
            if task.fid == fid:
                return task.get_file()
        # else:
        new_task = DownloadTask(FileStorage.fromFid(fid), self.__send__)
        self.tasks.append(new_task)
        return new_task.getFile()

    def cancel(self, fid):
        # packet = TrackerPacket.generatePacket(TrackerOperation.CANCEL,fid.encode())
        packet = TrackerReqPacket.newCancel(fid)
        packet = packet.toBytes()
        self.__send__(packet,self.tracker)
        # TODO our code

    def close(self):
        packet = TrackerReqPacket.newClose()
        packet = packet.toBytes()
        self.__send__(packet,self.tracker)
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

    time.sleep(1)
    PC1.close()

    PC1.cancel('000000481783c1907f8a1b5225abdbc0b395ad93')
    PC1.cancel('000000481783c1907f8a1b5225abdbc0b395ad93')
    PC2.cancel('000000481783c1907f8a1b5225abdbc0b395ad93')
    PC1.close()
    PC2.close()
    PC3.close()


