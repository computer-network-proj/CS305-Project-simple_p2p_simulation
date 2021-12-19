import time

from Packet import TrackerPacket,TrackerOperation
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
        threading.Thread(target=self.recvThread).start()
        #TODO our init code

    def recvThread(self):
        while self.active:
            packet, identification = self.__recv__()
            print(packet)

    def register(self, file_path: str):
        fileStorage = FileStorage.fromPath(file_path)
        byteFid = fileStorage.fid.encode()
        packet = TrackerPacket.generatePacket(TrackerOperation.REGISTER,byteFid)
        self.__send__(packet,self.tracker)

        # TODO our code


    def download(self, fid) -> bytes:
        # TODO 这里需要上线程锁
        # if task already exists:
        for task in self.tasks:
            if task.fid == fid:
                return task.get_file()
        # else:
        new_task = DownloadTask(FileStorage.fromFid(fid))
        self.tasks.append(new_task)
        return new_task.getFile()


    def cancel(self, fid):
        packet = TrackerPacket.generatePacket(TrackerOperation.CANCEL,fid.encode())
        self.__send__(packet,self.tracker)
        # TODO our code

    def close(self):
        pass
        # TODO our code


if __name__ == '__main__':
    tracker_address = ("127.0.0.1", 10086)
    # file_path = '../test_files/alice.txt'
    file_path = '../test_files/bg.png'
    proxy = Proxy(upload_rate=100000, download_rate=100000,port=10300)
    PC1 = ProjectPClient(tracker_address, upload_rate=100000, download_rate=100000)
    PC1.register(file_path)
    PC1.close()
    PC1.cancel('000000481783c1907f8a1b5225abdbc0b395ad93')
    PC1.cancel('000000481783c1907f8a1b5225abdbc0b395ad93')

    site = {'name': '我的博客地址', 'alexa': 10000, 'url': 'http://blog.csdn.net/uuihoo/'}
    pop_obj = site.pop('name')