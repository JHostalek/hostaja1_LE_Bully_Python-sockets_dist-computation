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
        self.message = "Requesting connection"


class AcceptConnectionMessage(Message):
    def __init__(self):
        super().__init__()
        self.message = "Accepting connection"


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


class TestMessage(Message):
    def __init__(self, message: str):
        super().__init__()
        self.message = message
