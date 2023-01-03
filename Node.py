from Message import NotifyAllMessage
from NetworkUtils import NetworkUtils


class Node:
    def __init__(self):
        self.nu = NetworkUtils(self)
        self.clock = 0
        self.nu.sendBroadcast(NotifyAllMessage(self).toBytes())

    def processBroadcast(self, message: NotifyAllMessage):
        print(f"Received message: {message.message} at logical time {message.clock} - {message.timestamp}")
        self.clock = max(self.clock, message.clock) + 1
