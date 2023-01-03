from Address import Address
from Message import TestMessage
from NetworkUtils import NetworkUtils


class Node:
    def __init__(self):
        self.nu = NetworkUtils(self)
        self.clock = 0
        self.neighbors = set()

    def processMessage(self, message: TestMessage, sender: Address):
        print(f"{self.nu.broadcastAddress} - Received message from {sender} : {message.message} at logical time {message.clock} - {message.timestamp}")
        self.clock = max(self.clock, message.clock) + 1
