import random
import threading
import time

import whisper

from Address import Address
from Message import ElectionMessage
from MessageReceiver import MessageReceiver
from MessageSender import MessageSender
from Network import Network
from Task import Task


class Node:
    def __init__(self):
        self.REAL_AUDIO = False
        self.state = None
        self.network = Network(self)
        self.sender = MessageSender(self.network)
        self.receiver = MessageReceiver(self.network)
        self.neighbors = set()
        self.leader = None
        self.leader_address = None
        self.MINIMUM_NEIGHBORS = 2
        self.WAIT_TIME = 10
        self.logicalClock = 0
        self.clockLock = threading.Lock()
        self.TAG = f'({self.logicalClock}) {self.network.IP}: '
        self.terminate = threading.Event()
        self.lock = threading.Lock()
        self.task_lock = threading.Lock()
        self.receiver.start()
        self.sender.sendConnectionRequest()
        self.work_thread = None

        self.task = None
        self.tasks = []
        self.NUMBER_OF_TASKS = 10
        for i in range(self.NUMBER_OF_TASKS):
            self.tasks.append(Task(i))
        self.result = {}
        self.got_response = False



    def setLeader(self, leader):
        if self.leader == leader: return
        self.leader = leader
        self.leader_address = Address((leader, self.network.PORT))
        if self.network.IP == leader:
            pass
        elif leader is not None:
            self.askForTask()

    def checkElection(self):
        if self.leader is None and self.state != 'ELECTION' and len(self.neighbors) >= self.MINIMUM_NEIGHBORS:
            print(f'{self.TAG}STARTING ELECTIONS - neighbors: {self.neighbors}')
            self.startElection()

    def removeNeighbor(self, ip):
        with self.lock:
            self.neighbors.remove(ip)
        print(f'{self.TAG}Removed {ip} from neighbors')
        if self.leader == ip:
            self.setLeader(None)
            self.checkElection()
            print(f'{self.TAG}{ip} is no longer the leader')

    # --------------------------------------------------------------------------------------------------------------
    def handleConnectionRequest(self, sender: Address):
        # existing network member
        receiver_address = Address((sender.ip, self.network.PORT))
        self.sender.sendConnectionAcceptance(receiver_address)

    def handleConnectionAcceptance(self, message, address):
        # incoming node
        if message.leader is not None:
            self.setLeader(message.leader)
        with self.lock:
            self.neighbors.add(address.ip)
        print(f'{self.TAG}Established connection with {address.id}, leader is {self.leader}')
        # finish handshake with the existing network member
        receiver_address = Address((address.ip, self.network.PORT))
        self.sender.sendConnectionEstablished(receiver_address)

    def handleConnectionEstablished(self, address):
        # existing network member
        with self.lock:
            self.neighbors.add(address.ip)
        print(f'{self.TAG}Established connection with {address.id}')

        # handshake with the incoming node finished check if we can start an election
        self.checkElection()
        if self.state == 'ELECTION':
            message = ElectionMessage()
            receiver_address = Address((address.ip, self.network.PORT))
            self.sender.send(message, receiver_address)

    # --------------------------------------------------------------------------------------------------------------
    def startElection(self):
        self.state = "ELECTION"
        self.sender.sendElectionMessage()
        time.sleep(self.WAIT_TIME)
        if self.state == "ELECTION" and self.leader is None:
            print(f"{self.TAG}I AM THE NEW LEADER")
            self.state = "COORDINATOR"
            self.setLeader(self.network.IP)
            receiver_address = Address((self.network.DATACENTER_IP, self.network.DATACENTER_PORT))
            self.sender.sendRequestCheckpointMessage(receiver_address)

    def handleElectionMessage(self, message, sender_address):
        # if self.leader is not None:
        #     print(f'{self.TAG}ERROR: Why am I receiving an election message from {sender_address}?')
        #     return
        if sender_address.ip < self.network.IP:
            receiver_address = Address((sender_address.ip, self.network.PORT))
            self.sender.sendAliveMessage(receiver_address)
        if self.state != "ELECTION":
            self.startElection()

    def handleVictoryMessage(self, message, address):
        self.state = "FOLLOWER"
        print(f"{self.TAG}NEW LEADER IS: {address.ip}")
        self.setLeader(address.ip)

    def handleAliveMessage(self, message, address):
        self.state = "WAITING"

    # --------------------------------------------------------------------------------------------------------------
    def getTask(self) -> int:

        for task in self.tasks:
            if task.state == 'NEW':
                with self.task_lock:
                    task.setBeingProcessed()
                return task.id
            elif task.state == 'PROCESSING' and task.getDuration() > 10:
                with self.task_lock:
                    task.setBeingProcessed()
                return task.id
        return -1

    def askForTask(self):
        if self.leader is not None:
            receiver_address = Address((self.leader, self.network.PORT))
            self.sender.sendTaskRequestMessage(receiver_address)
            prev_time = time.time()
            while True:
                if self.terminate.is_set():
                    return
                if self.got_response:
                    self.got_response = False
                    return
                if time.time() - prev_time > 10:
                    prev_time = time.time()
                    receiver_address = Address((self.leader, self.network.PORT))
                    self.sender.sendTaskRequestMessage(receiver_address)

    def handleTaskRequestMessage(self, message, address):
        self.checkAllDone()
        receiver_address = Address((address.ip, self.network.PORT))
        task = self.getTask()
        if task != -1:
            self.sender.sendTaskMessage(receiver_address, task)

    def handleTaskMessage(self, message, address):
        self.got_response = True
        print(f"{self.TAG}Received task: {message.task}")
        self.task = message.task
        receiver_address = Address((self.network.DATACENTER_IP, self.network.DATACENTER_PORT))
        self.sender.sendRequestAudioMessage(receiver_address, message.task)

    def handleAudioMessage(self, message, address):
        print(f"{self.TAG}Starting work on task: {self.task}")
        # work_thread = threading.Thread(target=self.processAudio, args=(self.leader, message.audio,))
        # work_thread.start()
        self.processAudio(self.leader, message.audio)

    def handleResultMessage(self, message, address):
        print(f"{self.TAG}Received result: {message.result}")
        self.tasks[message.task].result = message.result
        self.tasks[message.task].state = 'DONE'
        receiver_address = Address((self.network.DATACENTER_IP, self.network.DATACENTER_PORT))
        self.sender.sendCheckpointMessage(receiver_address, self.tasks)

        self.checkAllDone()

    def checkAllDone(self):
        for task in self.tasks:
            if task.state != 'DONE':
                return
        print(f"{self.TAG}All tasks done. Shutting down.")
        time.sleep(5)
        with self.lock:
            for n in self.neighbors:
                receiver_address = Address((n, self.network.PORT))
                self.sender.sendTerminateMessage(receiver_address)
        self.sender.sendTerminateMessage(Address((self.network.DATACENTER_IP, self.network.DATACENTER_PORT)))
        self.sender.terminate.set()
        self.receiver.terminate.set()
        self.terminate.set()

    def processAudio(self, current_leader, audio):
        print(f"{self.TAG}Processing audio {audio}...")
        if self.REAL_AUDIO:
            model = whisper.load_model('tiny.en')
            result = model.transcribe(audio, fp16=False, verbose=None)["text"]
        else:
            result = ''.join([chr(random.randint(97, 122)) for _ in range(10)])
        print(f"{self.TAG}Result: {result}")
        if self.leader != current_leader:
            print(f"{self.TAG}Leader changed, aborting")
            return
        receiver_address = Address((self.leader, self.network.PORT))
        self.sender.sendResultMessage(receiver_address, self.task, result)
        self.task = None
        self.askForTask()

    # --------------------------------------------------------------------------------------------------------------
    def handleCheckpointMessage(self, message, address):
        print(f"{self.TAG}Received checkpoint")
        if message.checkpoint is not None:
            self.tasks = message.checkpoint
        # Let other nodes know that we have the checkpoint, and we can start
        self.sender.sendVictoryMessage()

    # --------------------------------------------------------------------------------------------------------------
    def handleTerminateMessage(self, message, address):
        print(f"{self.TAG}Received terminate message")
        self.sender.terminate.set()
        self.receiver.terminate.set()
        self.terminate.set()
