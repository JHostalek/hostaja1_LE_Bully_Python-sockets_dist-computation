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
        self.category = "connection"
        self.message = "Requesting connection"


class AcceptConnectionMessage(Message):
    def __init__(self):
        super().__init__()
        self.category = "connection"
        self.message = "Accepting connection"


class ConnectionEstablishedMessage(Message):
    def __init__(self, leader: Address = None):
        super().__init__()
        self.category = "connection"
        self.message = "Established connection"
        self.leader = leader


class ElectionMessage(Message):
    def __init__(self):
        super().__init__()
        self.category = "election"
        self.message = "Election"


class AliveMessage(Message):
    def __init__(self):
        super().__init__()
        self.category = "election"
        self.message = "Alive"


class VictoryMessage(Message):
    def __init__(self):
        super().__init__()
        self.category = "election"
        self.message = "Victory"


class LeaderExistsMessage(Message):
    def __init__(self):
        super().__init__()
        self.category = "election"
        self.message = "Leader exists"
