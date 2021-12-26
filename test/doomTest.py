import time
from threading import Thread

from PClient import PClient

tracker_address = ("127.0.0.1", 10086)

if __name__ == '__main__':
    # A,B,C,D,E join the network
    A = PClient(tracker_address, upload_rate=200000, download_rate=50000, port=40001)
    B = PClient(tracker_address, upload_rate=50000, download_rate=100000, port=40002)
    C = PClient(tracker_address, upload_rate=100000, download_rate=50000, port=40003)
    D = PClient(tracker_address, upload_rate=70000, download_rate=40000, port=40004)
    E = PClient(tracker_address, upload_rate=200000, download_rate=700000, port=40005)

    # F = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40006)
    G = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40007)
    H = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40008)
    I = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40009)
    J = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40010)

    K = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40011)
    L = PClient(tracker_address, upload_rate=100000, download_rate=100000, port=40012)
    clients = [B, C, D, E, G, H, I, J]
    # A register a file and B download it
    fid = A.register("../test_files/bg.png")
    fid_two = A.register("../test_files/big_alice.txt")
    clients_1 = [E, G, H, I, J]
    threads = []
    files = {}
    files_1 = {}
    threads_1 = []


    # function for download and save
    def download(node, index):
        files[index] = node.download(fid)


    def download_1(node, index):
        files_1[index] = node.download(fid_two)


    time_start = time.time_ns()
    for i, client in enumerate(clients):
        threads.append(Thread(target=download, args=(client, i)))

    for i, client in enumerate(clients_1):
        threads.append(Thread(target=download_1, args=(client, i)))

    for t in threads_1:
        t.start()
    # start download in parallel
    for t in threads:
        t.start()

    time.sleep(10)
    A.close()
    time.sleep(5)
    L.register("../test_files/bg.png")
    K.register("../test_files/big_alice.txt")

    # wait for finish
    for t in threads:
        t.join()

    for t in threads_1:
        t.join()
    # check the downloaded files
    with open("../test_files/bg.png", "rb") as bg:
        bs = bg.read()
        for i in files:
            if files[i] != bs:
                raise Exception("Downloaded file is different with the original one")

    with open("../test_files/big_alice.txt", "rb") as bg:
        bss = bg.read()
        for i in files_1:
            if files_1[i] != bss:
                raise Exception("Downloaded file is different with the original one 1")
    # B, C, D, E has completed the download of file
    threads.clear()
    files = {}
    F = PClient(tracker_address, upload_rate=50000, download_rate=100000)
    # G = PClient(tracker_address, upload_rate=100000, download_rate=60000)
    # F, G join the network
    clients = [F, G]
    for i, client in enumerate(clients):
        threads.append(Thread(target=download, args=(client, i)))
    for t in threads:
        t.start()

    for t in threads:
        t.join()

    with open("../test_files/bg.png", "rb") as bg:
        bs = bg.read()
        for i in files:
            if files[i] != bs:
                raise Exception("Downloaded file is different with the original one")
    # A exits
    # time.sleep(20)
    # A.cancel(fid)

    # B exits
    time.sleep(10)
    B.close()

    # D exits
    time.sleep(30)
    D.close()
    for t in threads:
        t.join()
    for i in files:
        if files[i] != bs:
            raise Exception("Downloaded file is different with the original one")
    print("SUCCESS")

    # A.close()
    # B.close()
    C.close()
    # D.close()
    E.close()
    F.close()
    G.close()
    H.close()
    I.close()
    J.close()
    K.close()
    L.close()
    print((time.time_ns() - time_start) * 1e-9)
