import logging
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
    def __init__(self, data_center_ip, real_audio, tasks, message_delay, hold_each_message, bully_timeout, manual_ip):
        self.log = self.initLogger()
        self.hold_each_message = hold_each_message
        self.bully_timeout = bully_timeout
        self.REAL_AUDIO = real_audio
        self.manual_ip = manual_ip
        self.message_delay = message_delay
        self.state = None
        self.network = Network(self, data_center_ip, manual_ip)
        self.log.debug(f'----------------------------------------')
        self.log.debug(f'Initializing node {self.network.IP}...')
        self.sender = MessageSender(self.network)
        self.receiver = MessageReceiver(self.network)
        self.neighbors = set()
        self.leader = None
        self.leader_address = None
        self.MINIMUM_NEIGHBORS = 2
        self.logicalClock = 0
        self.clockLock = threading.Lock()
        self.TAG = f'{self.network.IP} - '
        self.terminate = threading.Event()
        self.lock = threading.Lock()
        self.task_lock = threading.Lock()
        self.receiver.start()
        self.sender.sendConnectionRequest()
        self.work_thread = None

        self.tasks = []
        self.NUMBER_OF_TASKS = tasks
        for i in range(self.NUMBER_OF_TASKS):
            self.tasks.append(Task(i))
        self.result = {}
        self.got_response = False
        self.task_timeout = 60 if self.REAL_AUDIO else 20

    def initLogger(self):
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)
        file_handler = logging.FileHandler('log.txt')
        logger.addHandler(file_handler)
        return logger

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
            self.log.debug(f'({self.logicalClock}) {self.TAG}STARTING ELECTIONS - neighbors: {self.neighbors}')
            self.startElection()

    def removeNeighbor(self, ip):
        with self.lock:
            self.neighbors.remove(ip)
        self.log.debug(f'({self.logicalClock}) {self.TAG}Removed {ip} from neighbors')
        if self.leader == ip:
            self.setLeader(None)
            self.checkElection()
            self.log.debug(f'({self.logicalClock}) {self.TAG}{ip} is no longer the leader')

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
        self.log.debug(f'({self.logicalClock}) {self.TAG}Established connection with {address.id}, leader is {self.leader}')
        # finish handshake with the existing network member
        receiver_address = Address((address.ip, self.network.PORT))
        self.sender.sendConnectionEstablished(receiver_address)

    def handleConnectionEstablished(self, address):
        # existing network member
        with self.lock:
            self.neighbors.add(address.ip)
        self.log.debug(f'({self.logicalClock}) {self.TAG}Established connection with {address.id}')

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
        time.sleep(self.bully_timeout)
        if self.state == "ELECTION" and self.leader is None:
            self.log.debug(f"({self.logicalClock}) {self.TAG}I AM THE NEW LEADER")
            self.state = "COORDINATOR"
            self.setLeader(self.network.IP)
            receiver_address = Address((self.network.DATACENTER_IP, self.network.DATACENTER_PORT))
            self.sender.sendRequestCheckpointMessage(receiver_address)

    def handleElectionMessage(self, message, sender_address):
        # if self.leader is not None:
        #     print(f'({self.logicalClock}) {self.TAG}ERROR: Why am I receiving an election message from {sender_address}?')
        #     return
        if sender_address.ip < self.network.IP:
            receiver_address = Address((sender_address.ip, self.network.PORT))
            self.sender.sendAliveMessage(receiver_address)
        if self.state != "ELECTION":
            self.startElection()

    def handleVictoryMessage(self, message, address):
        self.state = "FOLLOWER"
        self.log.debug(f"({self.logicalClock}) {self.TAG}NEW LEADER IS: {address.ip}")
        self.setLeader(address.ip)

    def handleAliveMessage(self, message, address):
        self.state = "WAITING"

    # --------------------------------------------------------------------------------------------------------------
    def getTask(self) -> int:
        for task in self.tasks:
            if task.state == 'NEW':
                task.setBeingProcessed()
                return task.id
            elif task.state == 'PROCESSING' and task.getDuration() > self.task_timeout:
                self.log.debug(f'({self.logicalClock}) {self.TAG}Task {task.id} is taking too long to process - {task.getDuration()}')
                task.setBeingProcessed()
                return task.id
        return -1

    def askForTask(self):
        if self.leader is not None:
            receiver_address = Address((self.leader, self.network.PORT))
            self.sender.sendTaskRequestMessage(receiver_address)
            prev_time = time.time()
            while True:
                time.sleep(0.5)
                if self.terminate.is_set():
                    return
                with self.lock:
                    if self.got_response:
                        self.got_response = False
                        return
                if time.time() - prev_time > 10:
                    self.log.debug(f'({self.logicalClock}) {self.TAG}Leader {self.leader} is not responding, sending another request')
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
        with self.lock:
            self.got_response = True
        self.log.debug(f"({self.logicalClock}) {self.TAG}Received task: {message.task}")
        receiver_address = Address((self.network.DATACENTER_IP, self.network.DATACENTER_PORT))
        self.sender.sendRequestAudioMessage(receiver_address, message.task)

    def handleAudioMessage(self, message, address):
        self.log.debug(f"({self.logicalClock}) {self.TAG}Starting work on task: {message.task}")
        # work_thread = threading.Thread(target=self.processAudio, args=(self.leader, message.audio,))
        # work_thread.start()
        self.processAudio(self.leader, message.audio, message.task)

    def handleResultMessage(self, message, address):
        self.log.debug(f"({self.logicalClock}) {self.TAG}Received result: {message.result}")
        self.tasks[message.task].result = message.result
        self.tasks[message.task].state = 'DONE'
        receiver_address = Address((self.network.DATACENTER_IP, self.network.DATACENTER_PORT))
        self.sender.sendCheckpointMessage(receiver_address, self.tasks)

        self.checkAllDone()

    def checkAllDone(self):
        for task in self.tasks:
            if task.state != 'DONE':
                return
        self.log.debug(f"({self.logicalClock}) {self.TAG}All tasks done. Shutting down.")
        time.sleep(5)
        with self.lock:
            for n in self.neighbors:
                receiver_address = Address((n, self.network.PORT))
                self.sender.sendTerminateMessage(receiver_address)
        self.sender.sendTerminateMessage(Address((self.network.DATACENTER_IP, self.network.DATACENTER_PORT)))
        self.sender.terminate.set()
        self.receiver.terminate.set()
        self.terminate.set()

    def processAudio(self, current_leader, audio, task):
        self.log.debug(f"({self.logicalClock}) {self.TAG}Processing audio {audio}...")
        if self.REAL_AUDIO:
            model = whisper.load_model('tiny.en')
            result = model.transcribe(audio, fp16=False, verbose=None)["text"]
        else:
            result = ''.join([chr(random.randint(97, 122)) for _ in range(10)])
            time.sleep(1)
        if self.leader != current_leader:
            self.log.debug(f"({self.logicalClock}) {self.TAG}Leader changed, aborting")
            return
        receiver_address = Address((self.leader, self.network.PORT))
        self.log.debug(f"({self.logicalClock}) {self.TAG}Sending result {result} to leader {self.leader}")
        self.sender.sendResultMessage(receiver_address, task, result)
        self.log.debug(f"({self.logicalClock}) {self.TAG}Before asking for new task")
        self.askForTask()
        self.log.debug(f"({self.logicalClock}) {self.TAG}After asking for new task")

    # --------------------------------------------------------------------------------------------------------------
    def handleCheckpointMessage(self, message, address):
        self.log.debug(f"({self.logicalClock}) {self.TAG}Received checkpoint")
        if message.checkpoint is not None:
            self.tasks = message.checkpoint
        # Let other nodes know that we have the checkpoint, and we can start
        self.sender.sendVictoryMessage()

    # --------------------------------------------------------------------------------------------------------------
    def handleTerminateMessage(self, message, address):
        self.log.debug(f"({self.logicalClock}) {self.TAG}Received terminate message")
        self.sender.terminate.set()
        self.receiver.terminate.set()
        self.terminate.set()
