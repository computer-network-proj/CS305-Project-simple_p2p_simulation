from Tracker import Tracker
from Packet import TrackerPacket, TrackerOperation





class ProjectTracker(Tracker):
    def __init__(self, upload_rate=10000, download_rate=10000, port=None):
        super().__init__(upload_rate, download_rate, port)
        self.SWITCH = {TrackerOperation.REGISTER: self.register,
                  TrackerOperation.DOWNLOAD: self.download,
                  TrackerOperation.CANCEL: self.cancel,
                  TrackerOperation.CLOSE: self.close}
        self.information = {}
        # TODO our code

    def start(self):

        while True:
            packet, identification = self.__recv__()
            print("Receive packet:{} from {}".format(packet, identification))
            header, type, info = TrackerPacket.generateInformation(packet)

            print(header)
            print(type)
            print(info)
            self.SWITCH.get(type,self.default)(info,identification)
        # TODO our code

    def register(self, fid, clientIdentification):
        fid = fid.decode()
        if fid not in self.information.keys():
            self.information[fid] = set()
            self.information[fid].add(clientIdentification)
        else:
            self.information[fid].add(clientIdentification)

        self.broadcast(fid)

    def download(self, fid, clientIdentification):
        fid = fid.decode()
        if fid not in self.information.keys():
            self.information[fid] = set()
            self.information[fid].add(clientIdentification)
        else:
            self.information[fid].add(clientIdentification)

        self.broadcast(fid)

    def cancel(self, fid, clientIdentification):
        fid = fid.decode()
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

    def close(self, fid,clientIdentification):
        for item in self.information.keys():
            self.cancel(item,clientIdentification)

    def broadcast(self,fid:str):
        receivers = self.information.get(fid)
        receivers = list(receivers)
        tempDictionary = {}
        tempDictionary[fid] = receivers
        sendData = str(tempDictionary)
        for item in receivers:
            self.response(sendData,item)

    def default(self,fid,clientIdentification):
        raise NotImplementedError()

    def response(self, data: str, address: (str, int)):
        self.__send__(data.encode(), address)

if __name__ == '__main__':
    tracker = ProjectTracker(port=10086)
    tracker.start()

        pass
        # TODO our code

