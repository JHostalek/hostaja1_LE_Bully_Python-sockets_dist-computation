import pickle
import time

import Node


class NotifyAllMessage:
    def __init__(self, sender: Node):
        self.message = "Notifying other nodes of my existence"
        self.clock = sender.clock
        self.timestamp = time.strftime("%H:%M:%S", time.localtime(time.time()))

    def toBytes(self):
        return pickle.dumps(self)
