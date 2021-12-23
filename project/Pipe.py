from queue import SimpleQueue
import time

'''
职能：构造send_queue和recv_queue进行代理。
'''


class Pipe:
    def __init__(self, rec_queue, send_queue):
        self.recv_queue = rec_queue
        self.send_queue = send_queue
        # self.send_func = send_func

    def send(self, data: bytes, dst: (str, int)):
        self.send_queue.put((data, dst))

    def recv(self, timeout=None) -> (bytes, (str, int)):
        while True:

            if not self.recv_queue.empty():
                return self.recv_queue.get()
            else:
                time.sleep(0.0000001)
