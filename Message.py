import abc
import pickle
import time


class Message(abc.ABC):
    def __init__(self):
        pass

    def toBytes(self):
        return pickle.dumps(self)


class RequestConnectionMessage(Message):
    def __init__(self):
        super().__init__()
        self.message = "Requesting connection"


class ConnectionAcceptanceMessage(Message):
    def __init__(self, leader: str):
        super().__init__()
        self.message = "Accepting connection"
        self.leader = leader


class ConnectionEstablishedMessage(Message):
    def __init__(self):
        super().__init__()
        self.message = "Established connection"


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


class TaskRequestMessage(Message):
    def __init__(self):
        super().__init__()
        self.message = "Requesting task"


class TaskMessage(Message):
    def __init__(self):
        super().__init__()
        self.message = "Sending task"
        self.task = str(time.time()).encode('utf-8').hex()[-8:]


class RequestAudioMessage(Message):
    def __init__(self):
        super().__init__()
        self.message = "Requesting audio"


class AudioMessage(Message):
    def __init__(self, audio):
        super().__init__()
        self.message = "Sending audio"
        self.audio = audio


class ResultMessage(Message):
    def __init__(self, task: id, result: str):
        super().__init__()
        self.message = "Sending result"
        self.task = task
        self.result = result
