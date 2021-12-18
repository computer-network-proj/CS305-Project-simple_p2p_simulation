'''
职能：实现文件存储，分片，智能选择
'''
import hashlib
import operator
import os
import random
import time

BLOCK_SIZE = 131072  # 16KB


def generateFidHead(str):
    return "%08d" % str


def MD5(data):
    md5obj = hashlib.md5()
    md5obj.update(data)
    dataHash = md5obj.hexdigest()
    return dataHash

class FileStorage:
    def __init__(self, filePieces=[], haveFilePieces=[], promises=[], fid=None):
        self.filePieces = filePieces
        self.haveFilePieces = haveFilePieces
        self.promises = promises
        self.fid = fid
        self.promisesMap = {}

    @staticmethod
    def generateFid(data):
        """
        以文件byte生成一个种子
        :param data: 文件bytes
        :return: 文件id
        """
        md5obj = hashlib.md5()
        md5obj.update(data)
        fid = md5obj.hexdigest()
        return fid

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
            promises.append(False)


        data_hash = FileStorage.generateFid(data)

        fid = generateFidHead(block_num) + data_hash

        fileStorage = FileStorage(filePieces=file_pieces,haveFilePieces=have_file_pieces,fid=fid,promises=promises)

        return fileStorage

    @staticmethod
    def fromFid(fid: str):
        """
        使用文件id生成一个FileStorage对象
        :param fid: 文件id
        :return: 一个FileStorage对象
        """
        block_num = int(fid[:8])
        filePieces = []
        haveFilePieces = []
        promises = []
        for i in range(block_num):
            filePieces.append(b"") #None
            haveFilePieces.append(False)
            promises.append(False)

        fileStorage = FileStorage(filePieces=filePieces,haveFilePieces=haveFilePieces,promises=promises,fid=fid)
        return fileStorage

    def isComplete(self):
        """
        判断文件是否完整
        :return: boolean值
        """
        checkFile = b""
        for item in self.filePieces:
            checkFile = checkFile+item
        fileHash = MD5(checkFile)
        if fileHash == self.fid[8:]:
            return True
        else:
            return False

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
        self.promises[index] = True
    def cancel(self, cid):
        """
        取消一个client对象的承诺。
        :param cid: client对象的id
        """
        self.promises[self.promisesMap[cid]] = False
        self.promisesMap.pop(cid)
        pass

    def promise(self, index, cid):
        """
        一个client对象许诺为我提供一个文件片
        :param index: 文件片段index
        :param cid: client对象的id
        """
        self.promisesMap[cid] = index
        self.promises[index] = True

    def isInteresting(self, haveFilePiecesOffered):
        """
        我是否对对方感兴趣
        :param haveFilePiecesOffered: 对方的haveFilePieces数组
        :return: boolean值
        """
        myPieces = set([i for i in range(int(self.fid[:8])) if self.haveFilePieces[i] == True])
        partnerPieces = set([i for i in range(int(self.fid[:8])) if haveFilePiecesOffered[i] == True])
        if partnerPieces > myPieces:
            return True
        else:
            return False

    def isInterested(self, haveFilePiecesOffered):
        """
        对方对我是否感兴趣
        :param haveFilePiecesOffered: 对方的haveFilePieces数组
        :return: boolean值
        """
        myPieces = set([i for i in range(int(self.fid[:8])) if self.haveFilePieces[i] == True])
        partnerPieces = set([i for i in range(int(self.fid[:8])) if haveFilePiecesOffered[i] == True])
        if myPieces > partnerPieces:
            return True
        else:
            return False

    def generateRequest(self, haveFilePiecesOffered):
        """
        随机寻找一个未被下载的文件片
        :param haveFilePiecesOffered: 对方的haveFilePieces数组
        :return: 文件片段index。如果找不到，返回-1
        """
        myPieces = set([i for i in range(int(self.fid[:8])) if self.haveFilePieces[i] == True])
        partnerPieces = set([i for i in range(int(self.fid[:8])) if haveFilePiecesOffered[i] == True])
        difference = partnerPieces.difference(myPieces)

        difference = list(difference)
        if len(difference) == 0:
            return -1
        else:
            return random.sample(difference,1)[0]




if __name__ == '__main__':
    print("hello python")

    # file_path = '../test_files/alice.txt'
    file_path = '../test_files/bg.png'
    file = FileStorage.fromPath(file_path)
    print(file.filePieces)
    b = b""
    for item in file.filePieces:
        b = b + item

    bin_file = open(file_path, 'rb')
    size = os.path.getsize(file_path)
    data_new = bin_file.read()
    bin_file.close()
    fid_new = FileStorage.generateFid(data_new)
    print(file.fid)
    print(fid_new)
    if data_new == b and fid_new ==file.fid[8:]:
        print("成功")
    else:
        print("失败")

    temp = FileStorage.fromFid("00000048")
    print(file.isComplete())
    print(temp.isComplete())


    #NOTE:test getFile
    print(temp.getFile())
    if file.getFile()==data_new:
        print("pass")

    #NOTE:test add
    temp.add(10,b"asasdasdasd")
    temp.add(11,b"asdasdas")
    temp.add(12,b"asdasdasd")

    #NOTE: test isInteresting and isInterested
    print(file.isInterested(temp.haveFilePieces))
    print(file.isInteresting(temp.haveFilePieces))
    print(temp.isInterested(file.haveFilePieces))
    print(temp.isInteresting(file.haveFilePieces))

    #NOTE:test generateRequest
    for i in range(500):
        # print(file.generateRequest(temp.haveFilePieces))
        if temp.generateRequest(file.haveFilePieces)==10:
            print("fail")
    # a = '123absg'
    # b = time.time()
    # c = '%s|%s' % (a, b)
    # print(c)
    # m = hashlib.md5()  # 调用hashlib里的md5()生成一个md5 hash对象
    # m.update(bytes(c, encoding='utf8'))  # 用update方法对字符串进行md5加密的更新处理
    #
    # result = m.hexdigest()  # 得出加密后的十六进制结果
    # print(result)
    #
    # print("---------------------------")
    # # 客户端
    # res = '%s|%s' % (result, b)
    # print(res)
    # # 服务端
    # get_result, get_time = res.split('|')
    # print(get_result)
    # print(b)
    # d = '%s|%s' % (a, get_time)  # 服务端将a和拿到的get_time进行拼接
    # n = hashlib.md5()
    # n.update(bytes(d, encoding='utf8'))  # 对拼接后的结果进行md5加密
    # s_result = m.hexdigest()  # 得出加密后的结果
    # print(s_result)
    # if s_result == get_result:  # 对比客户端传递过来的结果和服务端拼接加密后的结果进行比对
    #     print('验证通过')

    # def MD5(self,filepath):
    #     with open(filepath, 'rb') as f:
    #         md5obj = hashlib.md5()
    #         md5obj.update(f.read())
    #         hash = md5obj.hexdigest()
    #         return hash
