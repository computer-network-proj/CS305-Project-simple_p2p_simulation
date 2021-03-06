import threading
import time
import Packet as Packet

'''
职能：速度监控，top4+weak维护
'''


class TitForTat:
    def __init__(self, port):
        self.speed = {}
        self.top4 = []
        self.weak = None
        self.port = port
        self.operating = []
        threading.Thread(target=self._updateWeak, daemon=True).start()
        threading.Thread(target=self._monitoring_thread, daemon=True).start()

    def monitoring(self, packet):
        """
        此方法在收到包时被触发。以此实现流量监控。
        若包的类型是另一个Clinet传输的文件数据包，则加入速度监测的operating列表中。
        :param packet:
        """
        data, cid = packet
        if Packet.Packet.getType(data) == 4:
            self.operating.append(cid)

    def _monitoring_thread(self):
        """
        Exponential moving average, decay为手动设置设置超参 v_t = decay * v_{t-1} + (1 - decay) * theta_t
        使用滑动平均计算每秒收到包数
        :return:
        """
        while True:
            time.sleep(10)
            for o in self.operating:
                if o not in self.speed:
                    self.speed[o] = 0
                self.speed[o] += 1
            for o in self.speed:
                self.speed[o] /= 10
            # print(f"{self.port} receiving speed: {self.speed}\n", end="")
            self.operating.clear()

    def tryRegister(self, cid):
        """
        用户试图注册进入下载，完成top4或weak的更新，返回是否请求成功
        1. 尽可能更新top4，若top4为空则直接补上，若超过top4中最慢的则替换
        2. 若不可改变top4，假设weak为空就补上，否则抛弃
        :param cid:
        :return:
        """
        for c in self.top4:
            if self.speed[c] == 0:
                self.top4.remove(c)
        if cid not in self.speed:
            self.speed[cid] = 0
        if cid in self.top4:
            return True
        if len(self.top4) < 4:
            self.top4.append(cid)
            return True
        else:
            weakest_in_top4 = min(self.top4, key=lambda t: self.speed[t])
            if self.speed[cid] > self.speed[weakest_in_top4]:
                if cid not in self.speed:
                    self.speed[cid] = 0
                self.top4.remove(weakest_in_top4)
                self.top4.append(cid)
                return True
            else:
                if self.weak is None:
                    self.weak = cid
                    return True
                else:
                    return False

    def _updateWeak(self):
        """
        更新weak，每30秒一次
        1. 如果weak位client的速度超过top4中的，移去top4中最慢的一位加入weak位的client
        2. 将weak设为空等待新的加入者
        :return:
        """
        while True:
            time.sleep(30)
            if self.weak is None:
                continue
            weakest_in_top4 = min(self.top4, key=lambda c: self.speed[c])
            if self.speed[self.weak] > self.speed[weakest_in_top4]:
                self.top4.remove(weakest_in_top4)
                self.top4.append(self.weak)
            self.weak = None

    def isChoking(self, cid):
        """
        判断用户是否被choke
        :param cid:
        :return:
        """
        return cid != self.weak and cid not in self.top4

    def get_speed_of_top4(self):
        speed_str = f"Speed of Top 4 in {self.port}: \n"
        for cid in self.top4:
            speed_str += f"{cid[1]}: {round(self.speed[cid], 3)} "
        speed_str += "\n"
        return speed_str
