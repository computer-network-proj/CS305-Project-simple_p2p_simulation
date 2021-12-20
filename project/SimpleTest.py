# from PClient import PClient
from ProjectPClient import ProjectPClient as PClient

tracker_address = ("127.0.0.1", 10086)

if __name__ == '__main__':
    # A,B join the network
    A = PClient(tracker_address, upload_rate=2*1024*1024*1024, download_rate=2*1024*1024*1024)
    B = PClient(tracker_address, upload_rate=2*1024*1024*1024, download_rate=2*1024*1024*1024)

    # A register a file and B download it
    fid = A.register("../test_files/bg.png")
    data1 = B.download(fid)

    # A cancel the register of the file
    A.close()

    # C join the network and download the file from B
    C = PClient(tracker_address, upload_rate=100000, download_rate=100000)
    data2 = C.download(fid)

    if data1 == data2:
        print("Success!")
    else:
        raise RuntimeError

    B.close()
    C.close()
