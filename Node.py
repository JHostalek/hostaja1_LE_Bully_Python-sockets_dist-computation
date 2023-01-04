import threading
import time

from Address import Address
from MessageReceiver import MessageReceiver
from MessageSender import MessageSender
from Network import Network


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
        self.WAIT_TIME = 5
        self.TAG = self.network.IP + " - "
        self.terminate = threading.Event()
        self.lock = threading.Lock()
        self.receiver.start()
        self.sender.sendConnectionRequest()
        self.work_thread = None

    def setLeader(self, leader):
        if self.leader == leader: return
        self.leader = leader
        self.leader_address = Address((leader, self.network.PORT))
        if self.network.IP == leader:
            pass
        else:
            if self.work_thread is not None:
                self.work_thread.join()
            self.work_thread = threading.Thread(target=self.startWorking)
            self.work_thread.start()

    def checkElection(self):
        if self.leader is None and self.state != 'ELECTION' and len(self.neighbors) >= self.MINIMUM_NEIGHBORS:
            # time in forma hh:mm:ss
            print(f'{self.TAG}{time.strftime("%H:%M:%S")}STARTING ELECTIONS - neighbors: {self.neighbors}')
            self.startElection()

    # --------------------------------------------------------------------------------------------------------------
    def handleConnectionRequest(self, sender: Address):
        # existing network member
        receiver_address = Address((sender.ip, self.network.PORT))
        self.sender.sendConnectionAcceptance(receiver_address)

    def handleConnectionAcceptance(self, message, address):
        # incoming node
        if message.leader is not None:
            self.setLeader(message.leader)
        self.neighbors.add(address.ip)
        print(f'{self.TAG}Established connection with {address.id}, leader is {self.leader}')
        # finish handshake with the existing network member
        receiver_address = Address((address.ip, self.network.PORT))
        self.sender.sendConnectionEstablished(receiver_address)

    def handleConnectionEstablished(self, address):
        # existing network member
        self.neighbors.add(address.ip)
        print(f'{self.TAG}Established connection with {address.id}')

        # handshake with the incoming node finished check if we can start an election
        self.checkElection()

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
        if self.leader is not None:
            print(f'{self.TAG}ERROR: Why am I receiving an election message from {sender_address}?')
            return
        if self.state != "ELECTION":
            self.startElection()

        if sender_address.ip < self.network.IP:
            receiver_address = Address((sender_address.ip, self.network.PORT))
            self.sender.sendAliveMessage(receiver_address)

    def handleVictoryMessage(self, message, address):
        with self.lock:
            self.state = "FOLLOWER"
            self.setLeader(address.ip)
            print(f"{self.TAG}NEW LEADER IS: {self.leader}")

    def handleAliveMessage(self, message, address):
        with self.lock:
            self.state = "WAITING"

    # --------------------------------------------------------------------------------------------------------------
    def createTasks(self):
        pass

    def askForTask(self):
        receiver_address = Address((self.leader, self.network.PORT))
        self.sender.sendTaskRequestMessage(receiver_address)

    def startWorking(self):
        while not self.terminate.is_set():
            self.askForTask()
            time.sleep(5)

    def handleTaskRequestMessage(self, message, address):
        receiver_address = Address((address.ip, self.network.PORT))
        self.sender.sendTaskMessage(receiver_address)

    def handleTaskMessage(self, message, address):
        print(f"{self.TAG}Received task: {message.task}")
