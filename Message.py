import abc
import pickle
import time

import Node


class Message(abc.ABC):
    def __init__(self, sender: Node):
        self.timestamp = time.strftime("%H:%M:%S", time.localtime())
        self.clock = sender.clock

    def toBytes(self):
        return pickle.dumps(self)


class NotifyAllMessage(Message):
    def __init__(self, sender: Node):
        super().__init__(sender)
        self.message = "Notifying others of my existence"
