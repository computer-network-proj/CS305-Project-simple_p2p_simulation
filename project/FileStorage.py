'''
职能：实现文件存储，分片，智能选择
'''
import hashlib
import operator
import os
import random
import time
import threading

BLOCK_SIZE = 32 * 1024  # 现为128KB，可能设置16KB



# 输入数字，生成 8 位字符串
def generateFidHead(str):
    return int(str).to_bytes(length=4, byteorder="big")


def MD5(data: bytes):
    """
    输入byte串，返回其hash
    :param data: 类型为byte
    :return:
    """
    md5obj = hashlib.md5()
    md5obj.update(data)
    dataHash = md5obj.hexdigest()
    return dataHash


class FileStorage:
    def __init__(self, filePieces=[], haveFilePieces=[], promises=[], fid=None):
        """
        :param filePieces:
        :param haveFilePieces:
        :param promises:
        :param fid: str, 前8位为chunk数量，后为文件数据hash，作为文件id
        """
        self.filePieces = filePieces
        self.haveFilePieces = haveFilePieces
        self.promises = promises
        self.fid = fid
        self.max_timeout = 5
        self.closed = False
        self.timeoutThread = threading.Thread(target=self.timeout)
        self.timeoutThread.start()
        self.promisesMap = {}

    def close(self):
        self.closed = True

    def timeout(self):
        while not self.closed:
            time.sleep(1)
            for i in range(len(self.promises)):
                self.promises[i] = self.promises[i] - 1 if self.promises[i] > 0 else 0


    @staticmethod
    def generateFid(data: bytes):
        """
        以文件byte生成一个种子
        :param data: 文件bytes
        :return: 文件id
        """
        md5obj = hashlib.md5()
        md5obj.update(data)
        fileHash = md5obj.hexdigest()
        return fileHash

    @staticmethod
    def fromPath(path: str):
        """
        从文件路径生成一个FileStorage对象
        :param path: 文件路径
        :return: 一个FileStorage对象
        """
        bin_file = open(path, 'rb')
        size = os.path.getsize(path)
        data = bin_file.read()
        bin_file.close()
        block_num = size // BLOCK_SIZE if size % BLOCK_SIZE == 0 else size // BLOCK_SIZE + 1
        head = 0
        file_pieces = []
        have_file_pieces = []
        promises = []
        for item in range(block_num):
            file_pieces.append(data[item * BLOCK_SIZE:(item + 1) * BLOCK_SIZE])
            have_file_pieces.append(True)
            promises.append(0)

        data_hash = FileStorage.generateFid(data)
        header =generateFidHead(block_num)
        fid = header + data_hash.encode()

        fileStorage = FileStorage(filePieces=file_pieces, haveFilePieces=have_file_pieces, fid=fid, promises=promises)

        return fileStorage

    @staticmethod
    def fromFid(fid: str):
        """
        使用文件id生成一个FileStorage对象
        :param fid: 文件id
        :return: 一个FileStorage对象
        """
        # fid = fid.encode()
        block_num = int.from_bytes(fid[:4], byteorder="big")
        filePieces = []
        haveFilePieces = []
        promises = []
        for i in range(block_num):
            filePieces.append(b"")  # None
            haveFilePieces.append(False)
            promises.append(0)

        # fid = fid.decode()
        fileStorage = FileStorage(filePieces=filePieces, haveFilePieces=haveFilePieces, promises=promises, fid=fid)
        return fileStorage

    def isComplete(self):
        """
        判断文件是否完整
        :return: boolean值
        """
        checkFile = b""
        for item in self.filePieces:
            checkFile = checkFile + item
        fileHash = MD5(checkFile)
        return fileHash.encode() == self.fid[4:]

    def getFile(self):
        """
        返回文件
        :return: byte值。若文件不完整，返回None
        """
        fileTemp = b""
        if self.isComplete():
            for temp in self.filePieces:
                fileTemp = fileTemp + temp
            return fileTemp
        else:
            return None

    def add(self, index, data):
        """
        添加一个文件片段。
        :param index: 文件片段index
        :param data: 文件片段，byte值
        """
        self.filePieces[index] = data
        self.haveFilePieces[index] = True
        self.promises[index] = 0

    def cancel(self, cid):
        """
        取消一个client对象的承诺。
        :param cid: client对象的id
        """
        if cid in self.promisesMap.keys():
            popSet = self.promisesMap.pop(cid)
            for index in popSet:
                self.promises[index] = 0


    def promise(self, index, cid):
        """
        一个client对象许诺为我提供一个文件片
        :param index: 文件片段index
        :param cid: client对象的id
        """
        if cid not in self.promisesMap.keys():
            self.promisesMap[cid] =set()
            self.promisesMap[cid].add(index)
        else:
            self.promisesMap[cid].add(index)
        self.promises[index] = self.max_timeout

    def isInteresting(self, haveFilePiecesOffered):
        """
        我是否对对方感兴趣
        :param haveFilePiecesOffered: 对方的haveFilePieces数组
        :return: boolean值
        """
        have_temp = [ self.haveFilePieces[i] or self.promises[i] > 0 for i in range(len(self.haveFilePieces))]
        blockNum = int.from_bytes(self.fid[:4], byteorder="big")
        myPieces = set([i for i in range(blockNum) if have_temp[i] is True])
        partnerPieces = set([i for i in range(blockNum) if haveFilePiecesOffered[i] is True])
        return len(partnerPieces - myPieces) > 0

    # def isInterested(self, haveFilePiecesOffered):
    #     """
    #     对方对我是否感兴趣
    #     :param haveFilePiecesOffered: 对方的haveFilePieces数组
    #     :return: boolean值
    #     """
    #
    #     blockNum = int.from_bytes(self.fid[:4], byteorder="big")
    #     myPieces = set([i for i in range(blockNum) if self.haveFilePieces[i] == True])
    #     partnerPieces = set([i for i in range(blockNum) if haveFilePiecesOffered[i] == True])
    #
    #     return len(myPieces - partnerPieces) > 0

    def generateRequest(self, haveFilePiecesOffered):
        """.

        随机寻找一个未被下载的文件片
        :param haveFilePiecesOffered: 对方的haveFilePieces数组
        :return: 文件片段index。如果找不到，返回-1
        """
        #FIXME promise
        #BUG
        blockNum = int.from_bytes(self.fid[:4], byteorder="big")
        myPieces = set([i for i in range(blockNum) if self.haveFilePieces[i] == True])
        partnerPieces = set([i for i in range(blockNum) if haveFilePiecesOffered[i] == True])
        myPromises = set([i for i in range(blockNum) if self.promises[i] > 0])


        difference = partnerPieces - myPieces
        difference = difference - myPromises
        difference = list(difference)
        if len(difference) == 0:
            return -1
        else:
            return random.sample(difference, 1)[0]

    def display(self):
        string = ''
        for i in range(len(self.haveFilePieces)):
            if i % 10 == 0: string += ' '
            if self.haveFilePieces[i]:
                string += '#'
            elif self.promises[i] > 0:
                string += '+'
            else:
                string += '-'
        print(string)


if __name__ == '__main__':
    print("hello python")

    # file_path = '../test_files/alice.txt'
    file_path = '../test_files/bg.png'
    file = FileStorage.fromPath(file_path)
    # print(file.filePieces)
    b = b""
    for item in file.filePieces:
        b = b + item

    bin_file = open(file_path, 'rb')
    size = os.path.getsize(file_path)
    data_new = bin_file.read()
    bin_file.close()
    fid_new = FileStorage.generateFid(data_new).encode()
    print(file.fid)
    print(fid_new)
    if data_new == b and fid_new == file.fid[4:]:
        print("成功")
    else:
        print("失败")

    fid = file.fid
    temp = FileStorage.fromFid(fid)
    print(file.fid)
    print(file.isComplete())
    print(temp.isComplete())

    # NOTE:test getFile
    print(temp.getFile())
    if file.getFile() == data_new:
        print("pass")

    # NOTE:test add
    temp.add(10, b"asasdasdasd")
    temp.add(11, b"asdasdas")
    temp.add(12, b"asdasdasd")

    # NOTE: test isInteresting and isInterested
    # print(file.isInterested(temp.haveFilePieces))
    # print(file.isInteresting(temp.haveFilePieces))
    # print(temp.isInterested(file.haveFilePieces))
    # print(temp.isInteresting(file.haveFilePieces))

    # NOTE:test generateRequest
    for i in range(500):
        # print(file.generateRequest(temp.haveFilePieces))
        if temp.generateRequest(file.haveFilePieces) == 10:
            print("fail")
