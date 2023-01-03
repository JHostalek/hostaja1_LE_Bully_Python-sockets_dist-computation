import abc
import pickle

import Address
import Node


class Message(abc.ABC):
    def __init__(self):
        pass

    def toBytes(self):
        return pickle.dumps(self)


class RequestingConnection(Message):
    def __init__(self, sender: Node):
        super().__init__(sender)
        self.message = "Requesting connection"


class AcceptingConnection(Message):
    def __init__(self, sender: Node):
        super().__init__(sender)
        self.message = "Accepting connection"


class TestMessage(Message):
    def __init__(self, sender: Node, receiver: Address):
        super().__init__(sender)
        self.message = f'TCP test message from {sender.nu.ip} to {receiver}'
