from PClient import PClient
from DownloadTask import DownloadTask
import threading

class ProjectPClient(PClient):

    def __init__(self, tracker_addr: (str, int), proxy=None, port=None, upload_rate=0, download_rate=0):
        super().__init__(tracker_addr, proxy, port, upload_rate, download_rate)

        self.tasks = []
        threading.Thread(target=self.recvThread()).start()
        #TODO our init code

    def recvThread(self):
        while True:
            pass

    def register(self, file_path: str):
        pass
        # TODO our code


    def download(self, fid) -> bytes:
        # TODO 这里需要上线程锁
        # if task already exists:
        for task in self.tasks:
            if task.fid == fid:
                return task.get_file()
        # else:
        new_task = DownloadTask(fid)
        self.tasks.append(new_task)
        return new_task.getFile()


    def cancel(self, fid):
        pass
        # TODO our code

    def close(self):
        pass
        # TODO our code