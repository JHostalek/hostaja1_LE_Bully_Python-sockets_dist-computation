import time


class Task:
    def __init__(self, id: int):
        self.id = id
        self.result = None
        self.state = 'NEW'
        self.time = None
        self.time_ = None

    def setTime(self):
        # return time as hh:mm:ss
        self.time = time.strftime('%H:%M:%S', time.gmtime(self.time))
        self.time_ = time.time()

    def getDuration(self):
        # return duration in seconds
        print(self.time_ - time.time())
        return time.time() - self.time_

    def setBeingProcessed(self):
        self.state = 'PROCESSING'
        self.setTime()

    def setDone(self, result: str):
        self.state = 'DONE'
        self.result = result
        self.setTime()
