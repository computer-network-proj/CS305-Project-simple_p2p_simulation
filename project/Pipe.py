from queue import SimpleQueue

'''
职能：构造send_queue和recv_queue进行代理。
'''


class Pipe:
    def __init__(self):
        self.send_queue = SimpleQueue()
        self.recv_queue = SimpleQueue()

    def recv(self, timeout=None) -> (bytes, (str, int)):
        pass
        # TODO
