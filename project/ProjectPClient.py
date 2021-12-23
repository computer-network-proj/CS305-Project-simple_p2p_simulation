import signal
import time

from Packet import TrackerReqPacket, Packet, TrackerRespPacket, ClientRespPacket
from PClient import PClient
from DownloadTask import DownloadTask
from FileStorage import FileStorage
import threading
import  multiprocessing
from multiprocessing import SimpleQueue

from Proxy import Proxy


class ProjectPClient(PClient):

    def __init__(self, tracker_addr: (str, int), proxy=None, port=None, upload_rate=0, download_rate=0):
        super().__init__(tracker_addr, proxy, port, upload_rate, download_rate)
        self.active = True
        self.sub_process_send_queue = SimpleQueue()
        self.sub_process_recv_queue_dic = {}
        self.process = {}
        # self.tasks = {}
        self.file_map = {}
        self.lock = threading.Lock()

        threading.Thread(target=self.recvThread,daemon=True).start()
        threading.Thread(target=self.sendThread,daemon=True).start()
        # TODO our init code
    def sendThread(self):
        while self.active:
            # self.lock.acquire()
            pkt = self.sub_process_send_queue.get()
            if pkt[1][0] == "OUT_FILE":

                self.file_map[pkt[1][1]] = pkt[0]

            else:
                self.__send__(pkt[0],pkt[1])
            # self.lock.release()
            time.sleep(0.0001)

    def recvThread(self):
        while self.active:
            # self.lock.acquire()
            packet, cid = self.__recv__()
            packetType = Packet.getType(packet)

            fid = Packet.getFid(packet)

            if fid in self.sub_process_recv_queue_dic.keys():
                self.sub_process_recv_queue_dic[fid].put((packet, cid))
                if packetType == 4:
                    pass
                    # self.tasks[fid].fileStorage.display()
                    # pieces = self.tasks[fid].fileStorage.haveFilePieces
                    # print(str(cid[1]) + ' > ' + str(self.proxy.port) + " " + str(round(sum(pieces) / len(pieces), 5)) + "\n", end="")
                    # # print(self.tasks[fid].fileStorage.display())
            else:
                print("miss")
                print(str(cid[1]) + " > " + str(self.proxy.port))
                print(self.sub_process_recv_queue_dic.keys())
            # self.lock.release()


    def register(self, file_path: str):
        self.proxy.active = True
        # self.lock.acquire()
        fileStorage = FileStorage.fromPath(file_path)
        # packet = TrackerPacket.generatePacket(TrackerOperation.REGISTER,byteFid)
        fid = fileStorage.fid
        recv_queue = SimpleQueue()

        if fid in self.sub_process_recv_queue_dic:
            #TODO
            pass
            # self.tasks[fid].fileStorage = fileStorage
        else:
            self.sub_process_recv_queue_dic[fid] = recv_queue
            p = DownloadTask(fileStorage,recv_queue,self.sub_process_send_queue,self.proxy.port)
            p.daemon = False
            self.process[fid] = p
            p.start()

            packet = TrackerReqPacket.newRegister(fileStorage.fid)
            packet = packet.toBytes()
            self.__send__(packet, self.tracker)
        # self.lock.release()


        return fid

        # TODO our code

    def download(self, fid) -> bytes:
        # TODO 这里需要上线程锁
        # if task already exists:
        self.proxy.active = True
        recv_queue = SimpleQueue()
        self.lock.acquire()
        if fid in self.sub_process_recv_queue_dic:
            pass
            #TODO
        else:
            self.sub_process_recv_queue_dic[fid] = recv_queue
            p = DownloadTask(FileStorage.fromFid(fid),recv_queue,self.sub_process_send_queue,self.proxy.port)
            self.process[fid] = p
            p.daemon = False
            p.start()


            packet = TrackerReqPacket.newDownload(fid)
            packet = packet.toBytes()
            self.__send__(packet, self.tracker)
        self.lock.release()
        while True:
            time.sleep(1)
            if fid in self.file_map.keys():
                return self.file_map[fid]

    def cancel(self, fid):
        # self.lock.acquire()
        # packet = TrackerPacket.generatePacket(TrackerOperation.CANCEL,fid.encode())
        packet = TrackerReqPacket.newCancel(fid)
        packet = packet.toBytes()
        self.__send__(packet, self.tracker)

        tmp = self.process.pop(fid)
        sub_send = self.sub_process_recv_queue_dic.pop(fid)
        tmp.terminate()
        # self.lock.release()
        # TODO our code

    def close(self):
        # self.lock.acquire()
        packet = TrackerReqPacket.newClose()
        packet = packet.toBytes()
        self.__send__(packet, self.tracker)

        temp = self.process
        self.process= {}
        for key in temp.keys():
            temp[key].terminate()

        self.sub_process_recv_queue_dic ={}
        # self.lock.release()
        time.sleep(1)
        while True:
            if self.proxy.send_queue.qsize()==0:
                self.proxy.active = False
                break
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
