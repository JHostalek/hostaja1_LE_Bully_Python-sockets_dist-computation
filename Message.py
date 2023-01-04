import abc
import pickle

from Address import Address


class Message(abc.ABC):
    def __init__(self):
        pass

    def toBytes(self):
        return pickle.dumps(self)


class RequestConnectionMessage(Message):
    def __init__(self):
        super().__init__()
        self.message = "Requesting connection"


class ConnectionEstablishedMessage(Message):
    def __init__(self):
        super().__init__()
        self.message = "Established connection"


class AcceptConnectionMessage(Message):
    def __init__(self, leader: Address = None):
        super().__init__()
        self.message = "Accepting connection"
        self.leader = leader


class ElectionMessage(Message):
    def __init__(self):
        super().__init__()
        self.message = "Election"


class AliveMessage(Message):
    def __init__(self):
        super().__init__()
        self.message = "Alive"


class VictoryMessage(Message):
    def __init__(self):
        super().__init__()
        self.message = "Victory"


class LeaderExistsMessage(Message):
    def __init__(self):
        super().__init__()
        self.message = "Leader exists"


class TestMessage(Message):
    def __init__(self, message: str):
        super().__init__()
        self.message = message
