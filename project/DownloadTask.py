from Pipe import Pipe
from TitForTat import TitForTat
from Packet import ClientReqPacket, Packet, ClientRespPacket, TrackerRespPacket
import threading
from FileStorage import FileStorage
import time
import random

'''
职能：client对特定文件的维护类
'''


class DownloadTask:
    def __init__(self, fileStorage: FileStorage, send_func, selfPort=None):
        self.fid = fileStorage.fid
        self.peers = set()
        self.closed = False
        self.downloadingPeers = set()
        self.pipe = Pipe(send_func)
        self.titfortat = TitForTat()
        self.fileStorage = fileStorage
        self.selfPort = selfPort
        threading.Thread(target=self.run,daemon=True).start()
        threading.Thread(target=self._autoAsk,daemon=True).start()

    def close(self):
        self.closed = True

    def run(self):
        """
        实现recv的核心线程
        :return:
        """
        while not self.closed:
            packet = self.pipe.recv()
            self.titfortat.monitoring(packet)
            data, cid = packet
            type = Packet.getType(data)
            # tracker
            self.fileStorage.display()
            if type == 2:
                p = TrackerRespPacket.fromBytes(data)
                for c in self.peers - p.info:
                    self.fileStorage.cancel(c)
                print(f'{cid[1]} > {self.selfPort} | {p}\n', end='')
                self.peers = p.info
                self.downloadingPeers = self.downloadingPeers & self.peers
            elif type == 3:
                p = ClientReqPacket.fromBytes(data)
                print(f'{cid[1]} > {self.selfPort} | {p}\n', end='')
                if p.index == -1:
                    self.pipe.send(ClientRespPacket(self.fid, self.fileStorage.haveFilePieces, -1, b'').toBytes(), cid)
                else:
                    self.titfortat.tryRegister(cid)
                    able = not self.titfortat.isChoking(cid) and self.fileStorage.haveFilePieces[p.index]
                    if able:

                        print(f'{self.selfPort} send {cid[1]} {p.index}')
                        self.pipe.send(ClientRespPacket(self.fid, self.fileStorage.haveFilePieces, p.index, self.fileStorage.filePieces[p.index]).toBytes(), cid)
                    else:
                        self.pipe.send(ClientRespPacket(self.fid, self.fileStorage.haveFilePieces, -2, b'').toBytes(), cid)

            # get response
            elif type == 4:
                p = ClientRespPacket.fromBytes(data)
                print(f'{cid[1]} > {self.selfPort} | {p}\n', end='')
                if p.index == -2:
                    self.fileStorage.cancel(cid)
                    self.downloadingPeers.remove(cid)
                else:
                    if p.index != -1:
                        # if self.fileStorage.haveFilePieces[p.index]: continue
                        self.fileStorage.add(p.index, p.data)
                    if self.fileStorage.isInteresting(p.haveFilePieces):
                        chosenIndex = self.fileStorage.generateRequest(p.haveFilePieces)
                        if chosenIndex == -1: continue
                        print(f'{cid[1]} promise {self.selfPort} {chosenIndex}\n', end='')
                        self.fileStorage.promise(chosenIndex, cid)
                        self.pipe.send(ClientReqPacket(self.fileStorage.fid, chosenIndex).toBytes(), cid)

                        if self.fileStorage.isInteresting(p.haveFilePieces):
                            chosenIndex = self.fileStorage.generateRequest(p.haveFilePieces)
                            if chosenIndex == -1: continue
                            print(f'{cid[1]} promise {self.selfPort} {chosenIndex}\n', end='')
                            self.fileStorage.promise(chosenIndex, cid)
                            self.pipe.send(ClientReqPacket(self.fileStorage.fid, chosenIndex).toBytes(), cid)
                        else:
                            if cid in self.downloadingPeers : self.downloadingPeers.remove(cid)

                    else:
                        if cid in self.downloadingPeers: self.downloadingPeers.remove(cid)

                        # if self.pipe.recv_queue.qsize() > 0: continue
                        # if len(self.fileStorage.promisesMap[cid]) < 999999:
                        #     chosenIndex = self.fileStorage.generateRequest(p.haveFilePieces)
                        #     if chosenIndex == -1: continue
                        #     self.fileStorage.promise(chosenIndex, cid)
                        #     self.pipe.send(ClientReqPacket(self.fileStorage.fid, chosenIndex).toBytes(), cid)

    def _autoAsk(self):
        while not self.closed:
            if self.fileStorage.isComplete():
                return
            time.sleep(0.1)
            possiblePeers = list(self.peers - self.downloadingPeers - {('127.0.0.1', self.selfPort)})
            # print(str(self.selfPort) + " " + str(possiblePeers))

            if possiblePeers:
                randomPeerCid = random.choice(possiblePeers)
                self.pipe.send(ClientReqPacket(self.fileStorage.fid, -1).toBytes(), randomPeerCid)
                self.downloadingPeers.add(randomPeerCid)

    def getFile(self):
        """
        获取文件
        :return:
        """
        while not self.closed:
            time.sleep(0.01)
            if self.fileStorage.isComplete():
                return self.fileStorage.getFile()
