import time

from Message import NotifyAllMessage
from NetworkUtils import NetworkUtils


class Node:
    def __init__(self):
        self.nu = NetworkUtils()
        self.clock = 0
        self.nu.sendBroadcast(NotifyAllMessage(self).toBytes())
        self.send_keep_alive()

    def send_keep_alive(self):
        try:
            while True:
                time.sleep(5)
                self.nu.sendBroadcast(NotifyAllMessage(self).toBytes())
                self.clock += 1
        except KeyboardInterrupt:
            self.nu.terminate.set()
