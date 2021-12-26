import time
import threading
from Proxy import Proxy
from Packet import TrackerReqPacket, TrackerRespPacket


class Tracker:
    def __init__(self, upload_rate=10000, download_rate=10000, port=None):
        self.proxy = Proxy(upload_rate, download_rate, port)
        self.SWITCH = {1: self.register,
                       2: self.download,
                       3: self.cancel,
                       4: self.close}
        self.information = {}
        self.Tracker_lock = threading.Lock()

    def __send__(self, data: bytes, dst: (str, int)):
        """
        Do not modify this function!!!
        You must send all your packet by this function!!!
        :param data: The data to be send
        :param dst: The address of the destination
        """
        self.proxy.sendto(data, dst)

    def __recv__(self, timeout=None) -> (bytes, (str, int)):
        """
        Do not modify this function!!!
        You must receive all data from this function!!!
        :param timeout: if its value has been set, it can raise a TimeoutError;
                        else it will keep waiting until receive a packet from others
        :return: a tuple x with packet data in x[0] and the source address(ip, port) in x[1]
        """
        return self.proxy.recvfrom(timeout)

    def start(self):
        """
        Start the Tracker and it will work forever
        :return: None
        """
        # threading.Thread(target=self.autoBroadcast).start()
        while True:
            packet, identification = self.__recv__()
            print("Receive packet:{} from {}".format(packet, identification))

            # header, type, info = TrackerPacket.generateInformation(packet)
            packet = TrackerReqPacket.fromBytes(packet)
            type = packet.op
            info = packet.fid
            print(type, info)
            self.SWITCH.get(type, self.default)(info, identification)
            print(self.information)

    def register(self, fid, clientIdentification):
        self.Tracker_lock.acquire()
        if fid not in self.information.keys():
            self.information[fid] = set()
            self.information[fid].add(clientIdentification)
        else:
            self.information[fid].add(clientIdentification)
        self.broadcast(fid)
        self.Tracker_lock.release()

    def download(self, fid, clientIdentification):
        self.Tracker_lock.acquire()
        if fid not in self.information.keys():
            self.information[fid] = set()
            self.information[fid].add(clientIdentification)
        else:
            self.information[fid].add(clientIdentification)
        self.broadcast(fid)
        self.Tracker_lock.release()

    def cancel(self, fid, clientIdentification):
        self.Tracker_lock.acquire()
        if fid in self.information.keys():
            if clientIdentification in self.information[fid]:
                self.information[fid].remove(clientIdentification)
                if len(self.information[fid]) == 0:
                    self.information.pop(fid)
                else:
                    self.broadcast(fid)
            else:
                pass
        else:
            pass

        self.Tracker_lock.release()

    def close(self, fid, clientIdentification):
        self.Tracker_lock.acquire()
        broadcastList = []
        zeroList = []
        for item in self.information.keys():
            if clientIdentification in self.information[item]:
                self.information[item].remove(clientIdentification)
                if len(self.information[item]) == 0:
                    zeroList.append(item)
                else:
                    broadcastList.append(item)

        for fid in zeroList:
            self.information.pop(fid)

        for fid in broadcastList:
            self.broadcast(fid)
        self.Tracker_lock.release()

    def broadcast(self, fid: str):
        receivers = self.information.get(fid)
        # receivers = list(receivers)

        packet = TrackerRespPacket(fid, receivers)
        packet = packet.toBytes()
        print(receivers)
        for item in receivers:
            self.__send__(packet, item)

    def default(self, fid, clientIdentification):
        raise NotImplementedError()

    def autoBroadcast(self):
        while True:
            self.Tracker_lock.acquire()
            for fid in self.information.keys():
                self.broadcast(fid)
            self.Tracker_lock.release()
            print("广播")
            time.sleep(10)


if __name__ == '__main__':
    tracker = Tracker(port=10086, upload_rate=1000)
    tracker.start()
