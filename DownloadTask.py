from Pipe import Pipe
from Packet import ClientReqPacket, Packet, ClientRespPacket, TrackerRespPacket
from TitForTat import TitForTat
from FileStorage import FileStorage
import threading
import time
from multiprocessing import Process


'''
职能：client对特定文件的维护类
'''


class DownloadTask(Process):
    def __init__(self, fileStorage: FileStorage, rec_queue, send_queue,file_queue, selfPort=None, tit_tat=False):
        Process.__init__(self)

        self.fid = fileStorage.fid
        self.peers = set()
        self.closed = False
        self.downloadingPeers = set()
        self.pipe = Pipe(rec_queue, send_queue,file_queue)
        self.fileStorage = fileStorage
        self.selfPort = selfPort
        self.tit_tat = tit_tat

    def run(self):
        if self.tit_tat:
            self.titfortat = TitForTat(self.selfPort)
            # print("Outer" + str(self.selfPort) + str(self.titfortat))

        threading.Thread(target=self.run_sub).start()
        threading.Thread(target=self._autoAsk).start()
        threading.Thread(target=self.getFile).start()


    def run_sub(self):
        """
        实现recv的核心线程
        :return:
        """
        while not self.closed:
            packet = self.pipe.recv()
            self.opPacket(packet)

    def opPacket(self, packet):
        all = time.time()
        if self.tit_tat:
            self.titfortat.monitoring(packet)
        data, cid = packet
        type = Packet.getType(data)
        # tracker
        print(f'{self.selfPort}\t{self.fileStorage}\n', end='')
        if type == 2:
            p = TrackerRespPacket.fromBytes(data)
            for c in self.peers - p.info:
                self.fileStorage.cancel(c)
            # print(f'{cid[1]} > {self.selfPort} | {p}\n', end='')
            self.peers = p.info
            # self.downloadingPeers = self.downloadingPeers & self.peers
        elif type == 3:
            start = time.time()
            p = ClientReqPacket.fromBytes(data)
            # print(f'{cid[1]} > {self.selfPort} | {p}\n', end='')
            if p.index == -1:
                self.pipe.send(ClientRespPacket(self.fid, self.fileStorage.haveFilePieces, -1, b'').toBytes(), cid)
            else:
                if self.tit_tat:
                    self.titfortat.tryRegister(cid)
                    able = self.fileStorage.haveFilePieces[p.index] and not self.titfortat.isChoking(cid)
                    if self.titfortat.isChoking(cid):
                        # print(f"{self.selfPort} receiving speed: {self.titfortat.speed}\n")
                        print(self.titfortat.get_speed_of_top4() +
                              f"{self.selfPort} is choking {cid[1]}: {round(self.titfortat.speed[cid], 3)}\n",
                              end="")
                else:
                    able = self.fileStorage.haveFilePieces[p.index]
                if able:
                    # print(f'{self.selfPort} send {cid[1]} {p.index}')
                    self.pipe.send(ClientRespPacket(self.fid, self.fileStorage.haveFilePieces, p.index,
                                                    self.fileStorage.filePieces[p.index]).toBytes(), cid)
                else:
                    self.pipe.send(ClientRespPacket(self.fid, self.fileStorage.haveFilePieces, -2, b'').toBytes(), cid)

        # get response
        elif type == 4:
            start = time.time()
            p = ClientRespPacket.fromBytes(data)
            # print(f'{cid[1]} > {self.selfPort} | {p}\n', end='')
            if p.index == -2:
                self.fileStorage.cancel(cid)
                # self.downloadingPeers.remove(cid)
            else:
                if p.index == -1:
                    if not self.fileStorage.isInteresting(p.haveFilePieces) and \
                            cid in self.fileStorage.promisesMap.keys() and \
                            len(self.fileStorage.promisesMap[cid]) > 0:
                        self.fileStorage.cancel(cid)
                if p.index != -1:
                    if self.fileStorage.haveFilePieces[p.index]: return
                    self.fileStorage.add(p.index, p.data)
                if cid in self.fileStorage.promisesMap.keys() and len(self.fileStorage.promisesMap[cid]) > 2:
                    return
                if self.fileStorage.isInteresting(p.haveFilePieces):
                    chosenIndex = self.fileStorage.generateRequest(p.haveFilePieces, cid)
                    assert chosenIndex != -1
                    # print(f'{cid[1]} promise {self.selfPort} {chosenIndex}\n', end='')
                    self.fileStorage.promise(chosenIndex, cid)
                    self.pipe.send(ClientReqPacket(self.fileStorage.fid, chosenIndex).toBytes(), cid)
                else:
                    if cid in self.downloadingPeers: self.downloadingPeers.remove(cid)

            # print(f"??4-{time.time() - start}")
        # print(f'??A{time.time() - all}')

        # if self.pipe.recv_queue.qsize() > 0: continue
        # if len(self.fileStorage.promisesMap[cid]) < 999999:
        #     chosenIndex = self.fileStorage.generateRequest(p.haveFilePieces)
        #     if chosenIndex == -1: continue
        #     self.fileStorage.promise(chosenIndex, cid)
        #     self.pipe.send(ClientReqPacket(self.fileStorage.fid, chosenIndex).toBytes(), cid)

    def _autoAsk(self):
        while not self.closed:
            num = sum(self.fileStorage.promises)
            have_temp = [self.fileStorage.haveFilePieces[i] or self.fileStorage.promises[i] > 0 for i in range(len(self.fileStorage.haveFilePieces))]
            percent = sum(have_temp) / len(self.fileStorage.haveFilePieces)
            rest = len(have_temp) - sum(have_temp)
            # print(f"{self.selfPort} autoAsk {self.fileStorage.isComplete()}")
            if self.fileStorage.isComplete():
                return
            possiblePeers = list(self.peers - {('127.0.0.1', self.selfPort)})
            for peer in possiblePeers:
                self.pipe.send(ClientReqPacket(self.fileStorage.fid, -1).toBytes(), peer)

                if num < 2 and rest > 10 and percent < 0.5:

                    time.sleep(0.1)
                else:
                    time.sleep(1)
            time.sleep(0.1)

            # if possiblePeers:
            #     randomPeerCid = random.choice(possiblePeers)
            #     self.pipe.send(ClientReqPacket(self.fileStorage.fid, -1).toBytes(), randomPeerCid)
            #     self.pipe.send(ClientReqPacket(self.fileStorage.fid, -1).toBytes(), randomPeerCid)
            #     self.downloadingPeers.add(randomPeerCid)
            #     time.sleep(5)
            # time.sleep(1)

    def getFile(self):
        """
        获取文件
        :return:
        """
        while not self.closed:
            time.sleep(2)
            if self.fileStorage.isComplete():
                self.pipe.send_file(self.fileStorage.getFile(), ('OUT_FILE', self.fid))
                break
