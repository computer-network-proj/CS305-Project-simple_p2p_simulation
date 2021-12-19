from Pipe import Pipe
from TitForTat import TitForTat
import threading
from FileStorage import FileStorage
import time

'''
职能：client对特定文件的维护类
'''


class DownloadTask:
    def __init__(self, fileStorage: FileStorage):
        self.fid = fileStorage.fid
        self.pipe = Pipe()
        self.titfortat = TitForTat()
        self.fileStorage = fileStorage
        threading.Thread(target=self.run).start()

    def run(self):
        """
        实现recv的核心线程
        :return:
        """
        while True:
            packet = self.pipe.recv()
            self.titfortat.monitoring(packet)
            # TODO

    def getFile(self):
        """
        获取文件
        :return:
        """
        while True:
            time.sleep(0.01)
            if self.fileStorage.isComplete():
                return self.fileStorage.getFile()
