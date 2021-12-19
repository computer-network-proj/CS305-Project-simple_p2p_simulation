import threading
import time

'''
职能：速度监控，top4+week维护
'''


class TitForTat:
    def __init__(self):
        self.speed = {}
        self.top4 = []
        self.weak = None
        threading.Thread(target=self._updateWeak()).start()

    def monitoring(self, packet):
        """
        此方法在收到包时被触发。以此实现流量监控。
        :param packet:
        :return:
        """
        pass

    def tryRegister(self, cid):
        """
        用户试图注册进入下载
        :param cid:
        :return:
        """
        pass

    def _updateWeak(self):
        """
        更新week
        :return:
        """
        while True:
            time.sleep(30)
            pass

    def isChoking(self, cid):
        """
        判断用户是否被choke
        :param cid:
        :return:
        """
        return cid == self.weak or (cid in self.top4)
