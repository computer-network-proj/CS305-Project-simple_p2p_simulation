import time

from Packet import TrackerReqPacket, Packet, TrackerRespPacket, ClientRespPacket
from PClient import PClient
from DownloadTask import DownloadTask
from FileStorage import FileStorage
import threading
from multiprocessing import SimpleQueue
import multiprocessing
from Proxy import Proxy

lock  = threading.Lock
class ProjectPClient(PClient):

    def __init__(self, tracker_addr: (str, int), proxy=None, port=None, upload_rate=0, download_rate=0):
        super().__init__(tracker_addr, proxy, port, upload_rate, download_rate)
        self.active = True
        self.sub_process_send_queque = SimpleQueue()
        self.tasks = {}
        self.sub_process_receive_queque_dic = {}
        # self.fidMap = {}

        threading.Thread(target=self.recvThread).start()
        threading.Thread(target=self.sendThread).start()
        # TODO our init code

    def sendThread(self):
        while self.active:
            pkt = self.sub_process_send_queque.get()
            self.__send__(pkt[0],pkt[1])
            # for fid in self.tasks.keys():
            #     print(self.tasks.keys())
            #     print((self.proxy.port,fid))
            #     pkt = self.tasks[fid].pipe.send_queque.get()
            #     self.__send__(pkt[0],pkt[1])
            #     print("!!!!!!!!!!!!!!!!!!!!")
            time.sleep(0.0000001)

    def recvThread(self):
        while self.active:
            packet, cid = self.__recv__()
            packetType = Packet.getType(packet)
            print("--------------------------------------")
            fid = Packet.getFid(packet)
            if fid in self.sub_process_receive_queque_dic.keys():
                self.sub_process_receive_queque_dic[fid].put((packet, cid))
                # print("truecli",self)
                # print("task",self.tasks[fid].pipe.recv_queue)
                if packetType == 4:
                    pass
                    # self.tasks[fid].fileStorage.display()
                    # pieces = self.sub_process_receive_queque_dic[fid].fileStorage.haveFilePieces
                    # print(str(cid[1]) + ' > ' + str(self.proxy.port) + " " + str(round(sum(pieces) / len(pieces), 5)) + "\n", end="")
                    # # print(self.tasks[fid].fileStorage.display())
            else:
                print("miss")
                print(str(cid[1]) + " > " + str(self.proxy.port))
                print(self.sub_process_receive_queque_dic.keys())

    def register(self, file_path: str):
        sub_process_rec_queue = SimpleQueue()
        fileStorage = FileStorage.fromPath(file_path)
        # packet = TrackerPacket.generatePacket(TrackerOperation.REGISTER,byteFid)
        fid = fileStorage.fid
        if fid in self.sub_process_receive_queque_dic:
            pass
            #TODO
        else:
            DownloadTask(fileStorage,sub_process_rec_queue,self.sub_process_send_queque).start()
            self.sub_process_receive_queque_dic[fid] = sub_process_rec_queue

        packet = TrackerReqPacket.newRegister(fileStorage.fid)
        packet = packet.toBytes()
        self.__send__(packet, self.tracker)
        print("11111111111")
        return fid

        # TODO our code

    def download(self, fid) -> bytes:
        sub_process_rec_queue = SimpleQueue()
        # TODO 这里需要上线程锁
        # if task already exists:

        if fid in self.tasks:
            pass
            #TODO
            # return self.tasks[fid].get_file()

        # new_task = DownloadTask(FileStorage.fromFid(fid), self.__send__, selfPort=self.proxy.port, client=self)
        DownloadTask(FileStorage.fromFid(fid),sub_process_rec_queue,self.sub_process_send_queque).start()
        self.sub_process_receive_queque_dic[fid] = sub_process_rec_queue

        packet = TrackerReqPacket.newDownload(fid)
        packet = packet.toBytes()
        self.__send__(packet, self.tracker)
        #FIXME
        time.sleep(100)
        pass
        # return new_task.getFile()

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
        self.tasks = {}
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
