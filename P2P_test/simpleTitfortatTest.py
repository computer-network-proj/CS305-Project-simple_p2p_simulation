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
    A = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40001, tit_tat=False)
    B = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40002, tit_tat=True)
    C = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40003, tit_tat=True)
    D = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40004, tit_tat=True)
    E = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40005, tit_tat=True)

    F = PClient(tracker_address, upload_rate=10000, download_rate=300000, port=40006, tit_tat=False)
    G = PClient(tracker_address, upload_rate=10000, download_rate=300000, port=40007, tit_tat=False)
    H = PClient(tracker_address, upload_rate=10000, download_rate=300000, port=40008, tit_tat=False)

    fid = A.register("../test_files/largest_alice.txt")
    files = {}
    clients = [B, C, D, E, F, G, H]
    threads = []


    # function for download and save
    def download(node, index):
        files[index] = node.download(fid)


    for i, client in enumerate(clients):
        threads.append(Thread(target=download, args=(clients[i], i)))

    time_start = time.time_ns()
    for t in threads:
        t.start()

    time.sleep(100)
    F.proxy.upload_rate = 100000
    print("Improve Speed of F from 10kB/s to 100kB/s")
    for t in threads:
        t.join()
    # print(f"Time of P2P model: {(time.time_ns() - time_start) * 1e-9}")
    with open("../test_files/largest_alice.txt", "rb") as bg:
        bs = bg.read()
        for i in files:
            if files[i] != bs:
                raise Exception()

    A.close()
    for c in clients:
        c.close()
    print("End")
    print(f"Time of None Tit-for-Tat model: {(time.time_ns() - time_start) * 1e-9}")
