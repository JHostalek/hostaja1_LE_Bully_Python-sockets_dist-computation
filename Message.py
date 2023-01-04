import abc
import pickle


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


class ConnectionAcceptanceMessage(Message):
    def __init__(self, leader: str):
        super().__init__()
        self.category = "connection"
        self.message = "Accepting connection"
        self.leader = leader


class ConnectionEstablishedMessage(Message):
    def __init__(self):
        super().__init__()
        self.category = "connection"
        self.message = "Established connection"


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
