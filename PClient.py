from Proxy import Proxy
import time
from project.Packet import TrackerReqPacket, Packet, TrackerRespPacket, ClientRespPacket
from project.DownloadTask import DownloadTask
from project.FileStorage import FileStorage
import threading
from multiprocessing import SimpleQueue

class PClient:
    def __init__(self, tracker_addr: (str, int), proxy=None, port=None, upload_rate=0, download_rate=0, tit_tat=False):
        if proxy:
            self.proxy = proxy
        else:
            self.proxy = Proxy(upload_rate, download_rate, port)  # Do not modify this line!
        self.tracker = tracker_addr
        """
        Start your additional code below!
        """
        self.active = True
        self.sub_process_send_queue = SimpleQueue()
        self.sub_process_recv_queue_dic = {}
        self.process = {}
        self.file_map = {}
        self.lock = threading.Lock()
        self.tit_tat = tit_tat

        threading.Thread(target=self.recvThread,daemon=True).start()
        threading.Thread(target=self.sendThread,daemon=True).start()

    def sendThread(self):
        while self.active:
            pkt = self.sub_process_send_queue.get()
            if pkt[1][0] == "OUT_FILE":

                self.file_map[pkt[1][1]] = pkt[0]

            else:
                self.__send__(pkt[0],pkt[1])

            time.sleep(0.0001)

    def recvThread(self):
        while self.active:
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


    def __send__(self, data: bytes, dst: (str, int)):
        """
        Do not modify this function!!!
        You must send all your packet by this function!!!
        :param data: The data to be send
        :param dst: The address of the destination
        """
        self.proxy.sendto(data, dst)

    def __recv__(self, timeout=None) -> (bytes, (str, int)):
        """
        Do not modify this function!!!
        You must receive all data from this function!!!
        :param timeout: if its value has been set, it can raise a TimeoutError;
                        else it will keep waiting until receive a packet from others
        :return: a tuple x with packet data in x[0] and the source address(ip, port) in x[1]
        """
        return self.proxy.recvfrom(timeout)

    def register(self, file_path: str):
        """
        Share a file in P2P network
        :param file_path: The path to be shared, such as "./alice.txt"
        :return: fid, which is a unique identification of the shared file and can be used by other PClients to
                 download this file, such as a hash code of it
        """
        fid = None
        """
        Start your code below!
        """
        self.proxy.active = True

        fileStorage = FileStorage.fromPath(file_path)
        fid = fileStorage.fid
        recv_queue = SimpleQueue()

        if fid in self.sub_process_recv_queue_dic:
            pass
        else:
            self.sub_process_recv_queue_dic[fid] = recv_queue

            p = DownloadTask(fileStorage, recv_queue, self.sub_process_send_queue, self.proxy.port,
                             tit_tat=self.tit_tat)
            p.daemon = False
            self.process[fid] = p
            p.start()

            packet = TrackerReqPacket.newRegister(fileStorage.fid)
            packet = packet.toBytes()
            self.__send__(packet, self.tracker)

        """
        End of your code
        """
        return fid

    def download(self, fid) -> bytes:
        """
        Download a file from P2P network using its unique identification
        :param fid: the unique identification of the expected file, should be the same type of the return value of share()
        :return: the whole received file in bytes
        """
        data = None
        """
        Start your code below!
        """
        self.proxy.active = True
        recv_queue = SimpleQueue()
        self.lock.acquire()

        # if task already exists:
        if fid in self.sub_process_recv_queue_dic:
            pass
        else:
            self.sub_process_recv_queue_dic[fid] = recv_queue
            p = DownloadTask(FileStorage.fromFid(fid), recv_queue, self.sub_process_send_queue, self.proxy.port,
                             tit_tat=self.tit_tat)
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
        # """
        # End of your code
        # """
        # return data

    def cancel(self, fid):
        """
        Stop sharing a specific file, others should be unable to get this file from this client any more
        :param fid: the unique identification of the file to be canceled register on the Tracker
        :return: You can design as your need
        """
        packet = TrackerReqPacket.newCancel(fid)
        packet = packet.toBytes()
        self.__send__(packet, self.tracker)

        tmp = self.process.pop(fid)
        sub_send = self.sub_process_recv_queue_dic.pop(fid)
        tmp.terminate()
        """
        End of your code
        """

    def close(self):
        """
        Completely stop the client, this client will be unable to share or download files any more
        :return: You can design as your need
        """
        packet = TrackerReqPacket.newClose()
        packet = packet.toBytes()
        self.__send__(packet, self.tracker)

        temp = self.process
        self.process = {}
        for key in temp.keys():
            temp[key].terminate()

        self.sub_process_recv_queue_dic ={}
        time.sleep(1)
        while True:
            if self.proxy.send_queue.qsize()==0:
                self.proxy.close()
                break
        """
        End of your code
        """
        self.proxy.close()


if __name__ == '__main__':
    pass
