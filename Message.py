import abc
import pickle


class Message(abc.ABC):
    def __init__(self):
        pass

    def toBytes(self):
        return pickle.dumps(self)


class RequestingConnection(Message):
    def __init__(self):
        super().__init__()
        self.message = "Requesting connection"


class AcceptingConnection(Message):
    def __init__(self):
        super().__init__()
        self.message = "Accepting connection"


class TestMessage(Message):
    def __init__(self, message: str):
        super().__init__()
        self.message = message
