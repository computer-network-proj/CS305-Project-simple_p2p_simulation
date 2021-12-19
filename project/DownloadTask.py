from Pipe import Pipe
from TitForTat import TitForTat
import threading
from FileStorage import FileStorage
import time
import random

'''
职能：client对特定文件的维护类
'''


class DownloadTask:
    def __init__(self, fileStorage: FileStorage, send_func):
        self.fid = fileStorage.fid
        self.peers = set()
        self.downloadingPeers = set()
        self.pipe = Pipe(send_func)
        self.titfortat = TitForTat()
        self.fileStorage = fileStorage
        threading.Thread(target=self.run).start()
        threading.Thread(target=self._autoAsk).start()

    def run(self):
        """
        实现recv的核心线程
        :return:
        """
        while True:
            packet = self.pipe.recv()
            self.titfortat.monitoring(packet)
            # TODO

    def _autoAsk(self):
        while True:
            if self.fileStorage.isComplete():
                return
            time.sleep(0.1)
            possiblePeers = list(self.peers - self.downloadingPeers)
            if possiblePeers:
                randomPeerCid = random.choice(possiblePeers)
                # self.pipe.send()
                # TODO
                self.downloadingPeers.add(randomPeerCid)


    def getFile(self):
        """
        获取文件
        :return:
        """
        while True:
            time.sleep(0.01)
            if self.fileStorage.isComplete():
                return self.fileStorage.getFile()
