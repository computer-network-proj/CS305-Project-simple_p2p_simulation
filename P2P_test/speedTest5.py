import time
from threading import Thread

from PClient import PClient
from SC_model.client import Client
from SC_model.server import Server

tracker_address = ("127.0.0.1", 10086)


def client_download(client):
    client.download("../test_files/bg.png")


if __name__ == '__main__':
    # A, B, C, D, E join the network
    A = PClient(tracker_address, upload_rate=100000, download_rate=100000,port=40001)
    B = PClient(tracker_address, upload_rate=200000, download_rate=40000,port=40002)
    C = PClient(tracker_address, upload_rate=80000, download_rate=80000,port=40003)
    D = PClient(tracker_address, upload_rate=80000, download_rate=80000,port=40004)
    E = PClient(tracker_address, upload_rate=40000, download_rate=200000,port=40005)
    fid = A.register("../test_files/bg.png")
    files = {}
    clients = [B, C, D, E]
    threads = []

    # function for download and save
    def download(node, index):
        files[index] = node.download(fid)

    for i, client in enumerate(clients):
        threads.append(Thread(target=download, args=(clients[i], i)))

    time_start = time.time_ns()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"Time of P2P model: {(time.time_ns() - time_start) * 1e-9}")
    with open("../test_files/bg.png", "rb") as bg:
        bs = bg.read()
        for i in files:
            if files[i] != bs:
                raise Exception()

    A.close()
    for c in clients:
        c.close()
