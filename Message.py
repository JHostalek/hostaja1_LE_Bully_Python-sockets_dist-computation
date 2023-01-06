import abc
import pickle

from Task import Task


class Message(abc.ABC):
    def __init__(self):
        self.logicalClock = 0
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
    def __init__(self, task: int):
        super().__init__()
        self.message = "Sending task"
        self.task = task


class RequestAudioMessage(Message):
    def __init__(self, task: int):
        super().__init__()
        self.message = "Requesting audio"
        self.task = task


class AudioMessage(Message):
    def __init__(self, audio: str):
        super().__init__()
        self.message = "Sending audio"
        self.audio = audio


class ResultMessage(Message):
    def __init__(self, task: int, result: str):
        super().__init__()
        self.message = "Sending result"
        self.task = task
        self.result = result


class TerminateMessage(Message):
    def __init__(self):
        super().__init__()
        self.message = "Terminating"


class CheckpointMessage(Message):
    def __init__(self, checkpoint: [Task]):
        super().__init__()
        self.message = "Checkpoint"
        self.checkpoint = checkpoint


class RequestCheckpointMessage(Message):
    def __init__(self):
        super().__init__()
        self.message = "Requesting checkpoint"
