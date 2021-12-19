from queue import SimpleQueue
import time

'''
职能：构造send_queue和recv_queue进行代理。
'''


class Pipe:
    def __init__(self, send_func):
        self.recv_queue = SimpleQueue()
        self.send_func = send_func

    def send(self, data: bytes, dst: (str, int)):
        self.send_func(data, dst)

    def recv(self, timeout=None) -> (bytes, (str, int)):
        while True:
            time.sleep(0.001)
            if self.recv_queue:
                return self.recv_queue.get_nowait()
