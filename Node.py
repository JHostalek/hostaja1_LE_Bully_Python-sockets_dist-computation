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
        self.lock = threading.Lock()
        self.neighbors = set()
        self.leader = None
        self.leader_address = None
        self.MINIMUM_NEIGHBORS = 2
        self.WAIT_TIME = 5
        self.TAG = self.network.IP + " - "
        self.terminate = threading.Event()

    def setLeader(self, leader):
        self.leader = leader
        self.leader_address = Address((leader, self.network.PORT))

    def start(self):
        self.receiver.start()
        self.sender.start()
        self.sender.sendConnectionRequest()
        while not self.terminate.is_set():
            # time as hh:mm:ss
            print(f'{self.TAG}TIME: {time.strftime("%H:%M:%S", time.localtime())}')
            self.receiver.consume()

    def stop(self):
        self.terminate.set()
        self.sender.stop()
        self.receiver.stop()

    def checkElection(self):
        if self.leader is None and len(self.neighbors) >= self.MINIMUM_NEIGHBORS:
            print(f'{self.TAG}STARTING ELECTIONS - neighbors: {self.neighbors}')
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
        self.sender.sendConnectionEstablished(address)

        # incoming node is ready
        self.checkElection()

    def handleConnectionEstablished(self, address):
        # existing network member
        self.neighbors.add(address.ip)
        print(f'{self.TAG}Established connection with {address.id}')

        # handshake with the incoming node finished check if we can start an election
        self.checkElection()

    # --------------------------------------------------------------------------------------------------------------
    def startElection(self):
        self.state = "ELECTION"
        self.sender.sendElectionMessage()
        time.sleep(self.WAIT_TIME)
        if self.state == "ELECTION":
            print(f"{self.TAG}I AM THE NEW LEADER")
            self.state = "COORDINATOR"
            self.setLeader(self.network.IP)
            self.sender.sendVictoryMessage()

    def handleElectionMessage(self, message, sender_address):
        if self.leader is not None:
            print(f'{self.TAG}ERROR: Why am I receiving an election message from {sender_address}?')
            return
        if self.state != "ELECTION":
            self.startElection()
        if sender_address.ip < self.network.IP:
            self.sender.sendAliveMessage(sender_address)

    def handleVictoryMessage(self, message, address):
        self.state = "FOLLOWER"
        self.setLeader(address.ip)
        print(f"{self.TAG}ELECTION FINISHED - LEADER IS: {self.leader}")

    def handleAliveMessage(self, message, address):
        self.state = "WAITING"
