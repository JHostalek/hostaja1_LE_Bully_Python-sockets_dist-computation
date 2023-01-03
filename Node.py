from Address import Address
from Message import NotifyAllMessage, Message, TestMessage
from NetworkUtils import NetworkUtils


class Node:
    def __init__(self):
        self.nu = NetworkUtils(self)
        self.clock = 0
        self.neighbors = set()
        self.nu.sendBroadcast(NotifyAllMessage(self).toBytes())

    def processBroadcast(self, message: Message, sender: Address):
        print(f"{self.nu.broadcastAddress} - Received message from {sender} : {message.message} at logical time {message.clock} - {message.timestamp}")
        self.clock = max(self.clock, message.clock) + 1
        self.neighbors |= {sender}
        print(f"{self.nu.broadcastAddress} - My neighbors are {self.neighbors}")
        for neighbor in self.neighbors:
            target = Address((neighbor.ip, self.nu.PORT))
            self.nu.send(TestMessage(self, neighbor).toBytes(), target)

    def processMessage(self, message: Message, sender: Address):
        pass
