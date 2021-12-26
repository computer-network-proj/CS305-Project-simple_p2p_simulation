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
    A = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40001)
    B = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40002)
    C = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40003)
    D = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40004)
    E = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40005)

    F = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40006)
    G = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40007)
    H = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40008)
    I = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40009)
    J = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40010)
    K = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40011)

    L = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40012)
    M = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40013)
    N = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40014)
    O = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40015)
    P = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40016)

    fid = A.register("../test_files/bg.png")

    # K.register("../test_files/big_alice.txt")
    files = {}
    clients = [B, C, D, E, F, G, H, I, J, K, L, M, N, O, P]
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
    print("SUCCESS")
    A.close()
    # K.close()
    for c in clients:
        c.close()

    print("Ending")
