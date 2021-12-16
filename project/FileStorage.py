
'''
职能：实现文件存储，分片，智能选择
'''
class FileStorage:
    def __init__(self):
        self.filePieces = []
        self.haveFilePieces = []
        self.promises = []
        self.fid = None

    @staticmethod
    def generateFid(data):
        """
        以文件byte生成一个种子
        :param data: 文件bytes
        :return: 文件id
        """
        pass

    @staticmethod
    def fromPath(path: str):
        """
        从文件路径生成一个FileStorage对象
        :param path: 文件路径
        :return: 一个FileStorage对象
        """
        pass

    @staticmethod
    def fromFid(fid: str):
        """
        使用文件id生成一个FileStorage对象
        :param fid: 文件id
        :return: 一个FileStorage对象
        """
        pass

    def isComplete(self):
        """
        判断文件是否完整
        :return: boolean值
        """
        pass

    def getFile(self):
        """
        返回文件
        :return: byte值。若文件不完整，返回None
        """
        pass

    def add(self, index, data):
        """
        添加一个文件片段。
        :param index: 文件片段index
        :param data: 文件片段，byte值
        """
        pass

    def cancel(self, cid):
        """
        取消一个client对象的承诺。
        :param cid: client对象的id
        """
        pass

    def promise(self, index, cid):
        """
        一个client对象许诺为我提供一个文件片
        :param index: 文件片段index
        :param cid: client对象的id
        """
        pass

    def isInteresting(self, haveFilePiecesOffered):
        """
        我是否对对方感兴趣
        :param haveFilePiecesOffered: 对方的haveFilePieces数组
        :return: boolean值
        """
        pass

    def isInterested(self, haveFilePiecesOffered):
        """
        对方对我是否感兴趣
        :param haveFilePiecesOffered: 对方的haveFilePieces数组
        :return: boolean值
        """
        pass

    def generateRequest(self, haveFilePiecesOffered):
        """
        随机寻找一个未被下载的文件片
        :param haveFilePiecesOffered: 对方的haveFilePieces数组
        :return: 文件片段index。如果找不到，返回-1
        """
        pass