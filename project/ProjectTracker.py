from Tracker import Tracker
from Packet import TrackerReqPacket, TrackerRespPacket


class ProjectTracker(Tracker):
    def __init__(self, upload_rate=10000, download_rate=10000, port=None):
        super().__init__(upload_rate, download_rate, port)
        self.SWITCH = {1: self.register,
                       2: self.download,
                       3: self.cancel,
                       4: self.close}
        self.information = {}
        # TODO our code

    def start(self):
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
        # TODO our code

    def register(self, fid, clientIdentification):
        if fid not in self.information.keys():
            self.information[fid] = set()
            self.information[fid].add(clientIdentification)
        else:
            self.information[fid].add(clientIdentification)

        self.broadcast(fid)

    def download(self, fid, clientIdentification):
        if fid not in self.information.keys():
            self.information[fid] = set()
            self.information[fid].add(clientIdentification)
        else:
            self.information[fid].add(clientIdentification)

        self.broadcast(fid)

    def cancel(self, fid, clientIdentification):
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

    def close(self, fid, clientIdentification):
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

    # def response(self, data: str, address: (str, int)):
    #     self.__send__(data.encode(), address)


if __name__ == '__main__':
    tracker = ProjectTracker(port=10086)
    tracker.start()

    # TODO our code
