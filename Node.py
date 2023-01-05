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
        self.state = None
        self.network = Network(self)
        self.sender = MessageSender(self.network)
        self.receiver = MessageReceiver(self.network)
        self.neighbors = set()
        self.leader = None
        self.leader_address = None
        self.MINIMUM_NEIGHBORS = 2
        self.WAIT_TIME = 10
        self.TAG = self.network.IP + " - "
        self.terminate = threading.Event()
        self.lock = threading.Lock()
        self.receiver.start()
        self.sender.sendConnectionRequest()
        self.work_thread = None

        self.task = -1
        self.tasks = []
        for i in range(20):
            self.tasks.append(Task(i))
        self.result = {}

    def setLeader(self, leader):
        if self.leader == leader: return
        self.leader = leader
        self.leader_address = Address((leader, self.network.PORT))
        if self.network.IP == leader:
            pass
        else:
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
        with self.lock:
            self.state = "ELECTION"
        self.sender.sendElectionMessage()
        time.sleep(self.WAIT_TIME)
        if self.state == "ELECTION" and self.leader is None:
            print(f"{self.TAG}I AM THE NEW LEADER")
            with self.lock:
                self.state = "COORDINATOR"
                self.setLeader(self.network.IP)
            self.sender.sendVictoryMessage()
            time.sleep(5)

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
        with self.lock:
            self.state = "FOLLOWER"
            self.setLeader(address.ip)
            print(f"{self.TAG}NEW LEADER IS: {self.leader}")

    def handleAliveMessage(self, message, address):
        with self.lock:
            self.state = "WAITING"

    # --------------------------------------------------------------------------------------------------------------
    def getTask(self) -> int:
        with self.lock:
            for task in self.tasks:
                if task.state == 'NEW':
                    return task.id
                elif task.state == 'IN_PROGRESS' and task.getDuration() > 20:
                    return task.id
                else:
                    raise Exception("No task available")

    def askForTask(self):
        if self.leader is not None:
            receiver_address = Address((self.leader, self.network.PORT))
            self.sender.sendTaskRequestMessage(receiver_address)

    def handleTaskRequestMessage(self, message, address):
        receiver_address = Address((address.ip, self.network.PORT))
        self.sender.sendTaskMessage(receiver_address, self.getTask())

    def handleTaskMessage(self, message, address):
        print(f"{self.TAG}Received task: {message.task}")
        self.task = message.task
        receiver_address = Address((self.network.DATACENTER_IP, self.network.DATACENTER_PORT))
        self.sender.sendRequestAudioMessage(receiver_address, message.task)

    def handleAudioMessage(self, message, address):
        print(f"{self.TAG}Starting work on task: {message.task}")
        work_thread = threading.Thread(target=self.processAudio, args=(self.leader, message.audio,))
        work_thread.start()

    def handleResultMessage(self, message, address):
        print(f"{self.TAG}Received result: {message.result}")
        self.result[message.task] = message.result
        with self.lock:
            # print(''.join([self.result[key] for key in sorted(self.result)]))
            print(self.result)

    def processAudio(self, current_leader, audio):
        print(f"{self.TAG}Processing audio...")
        model = whisper.load_model('tiny.en')
        result = model.transcribe(audio, fp16=False)["text"]
        print(f"{self.TAG}Result: {result}")
        if self.leader != current_leader:
            print(f"{self.TAG}Leader changed, aborting")
            return
        receiver_address = Address((self.leader, self.network.PORT))
        self.sender.sendResultMessage(receiver_address, self.task, result)
        self.task = None
        self.askForTask()
