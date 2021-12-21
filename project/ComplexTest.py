import time
from threading import Thread

from ProjectPClient import ProjectPClient as PClient

tracker_address = ("127.0.0.1", 10086)

if __name__ == '__main__':
    # A,B,C,D,E join the network
    A = PClient(tracker_address, upload_rate=2000000, download_rate=500000, port=10091)
    B = PClient(tracker_address, upload_rate=500000, download_rate=1000000, port=10092)
    C = PClient(tracker_address, upload_rate=1000000, download_rate=500000, port=10093)
    D = PClient(tracker_address, upload_rate=700000, download_rate=400000, port=10094)
    E = PClient(tracker_address, upload_rate=2000000, download_rate=7000000, port=10095)

    clients = [B, C, D, E]
    # A register a file and B download it
    fid = A.register("../test_files/alice.txt")
    threads = []
    files = {}


    # function for download and save
    def download(node, index):
        files[index] = node.download(fid)


    time_start = time.time_ns()
    for i, client in enumerate(clients):
        threads.append(Thread(target=download, args=(client, i)))
    # start download in parallel
    for t in threads:
        t.start()
    # wait for finish
    for t in threads:
        t.join()
    # check the downloaded files
    with open("../test_files/alice.txt", "rb") as bg:
        bs = bg.read()
        for i in files:
            if files[i] != bs:
                raise Exception("Downloaded file is different with the original one")

    # exit()
    # B, C, D, E has completed the download of file
    threads.clear()
    print("-------------------------------")

    F = PClient(tracker_address, upload_rate=500000, download_rate=1000000, port=10096)
    G = PClient(tracker_address, upload_rate=1000000, download_rate=600000, port=10097)
    # F, G join the network
    clients = [F, G]
    for i, client in enumerate(clients):
        threads.append(Thread(target=download, args=(client, i)))
    for t in threads:
        t.start()

    # A exits
    time.sleep(20)
    A.cancel(fid)
    print("A cancel")

    # B exits
    time.sleep(10)
    B.close()
    print("B close")

    # D exits
    time.sleep(30)
    D.close()
    print("D close")
    for t in threads:
        t.join()
    for i in files:
        if files[i] != bs:
            raise Exception("Downloaded file is different with the original one")
    print("SUCCESS")

    A.close()
    C.close()
    E.close()
    F.close()
    G.close()
    print((time.time_ns() - time_start) * 1e-9)
