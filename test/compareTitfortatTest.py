import time
from threading import Thread

from PClient import PClient

tracker_address = ("127.0.0.1", 10086)


def client_download(client):
    client.download("../test_files/bg.png")


if __name__ == '__main__':
    # Tit-for-tat Test
    A1 = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=50001, tit_tat=True)
    B1 = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=50002, tit_tat=True)
    C1 = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=50003, tit_tat=True)
    D1 = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=50004, tit_tat=True)
    E1 = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=50005, tit_tat=True)
    F1 = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=50006, tit_tat=True)
    G1 = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=50007, tit_tat=True)
    H1 = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=50008, tit_tat=True)

    fid = A1.register("../test_files/bg.png")
    files = {}
    clients = [B1, C1, D1, E1, F1, G1, H1]
    threads = []


    def download(node, index):
        files[index] = node.download(fid)


    for i, client in enumerate(clients):
        threads.append(Thread(target=download, args=(clients[i], i)))

    time_start = time.time_ns()
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"Time of Tit-for-Tat model: {(time.time_ns() - time_start) * 1e-9}")

    with open("../test_files/bg.png", "rb") as bg:
        bs = bg.read()
        for i in files:
            if files[i] != bs:
                raise Exception()

    A1.close()
    for c in clients:
        c.close()

    # None Tit-for-tat Test
    A2 = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=60001, tit_tat=False)
    B2 = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=60002, tit_tat=False)
    C2 = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=60003, tit_tat=False)
    D2 = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=60004, tit_tat=False)
    E2 = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=60005, tit_tat=False)
    F2 = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=60006, tit_tat=False)
    G2 = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=60007, tit_tat=False)
    H2 = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=60008, tit_tat=False)

    fid = A2.register("../test_files/bg.png")
    files = {}
    clients = [B2, C2, D2, E2, F2, G2, H2]
    threads = []

    for i, client in enumerate(clients):
        threads.append(Thread(target=download, args=(clients[i], i)))

    time_start = time.time_ns()
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"Time of None Tit-for-Tat model: {(time.time_ns() - time_start) * 1e-9}")

    with open("../test_files/bg.png", "rb") as bg:
        bs = bg.read()
        for i in files:
            if files[i] != bs:
                raise Exception()

    A2.close()
    for c in clients:
        c.close()
