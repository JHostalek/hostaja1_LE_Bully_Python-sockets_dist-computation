import socket
import threading

import Network
from Address import Address
from Message import *


class MessageSender:
    def __init__(self, network: Network):
        self.network = network
        self.node = network.node
        self.TAG = self.network.IP + " - "
        self.terminate = threading.Event()

    def sendBroadcast(self, message: Message):
        receiver_address = (self.network.BROADCAST_IP, self.network.BROADCAST_PORT)
        self.network.broadcastSocket.sendto(message.toBytes(), receiver_address)

    def send(self, message: Message, receiver_address: Address):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(receiver_address.address)
            client.send(message.toBytes())
            client.close()
        except ConnectionError:
            print(self.TAG + "Connection error by " + str(receiver_address))
            if receiver_address in self.node.neighbors:
                self.node.neighbors.remove(receiver_address)
                print(self.TAG + "Removed " + str(receiver_address) + " from neighbors")
                if self.node.state == 'ELECTION':
                    self.node.state = None
            if receiver_address.ip == self.node.leader:
                self.node.leader = None
                self.node.checkElection()
                print(self.TAG + str(receiver_address) + " is no longer the leader")
        except socket.timeout:
            print(self.TAG + "Connection timeout by " + str(receiver_address))

    # --------------------------------------------------------------------------------------------------------------
    def sendConnectionRequest(self):
        # BROADCAST CONNECTION REQUEST
        message = RequestConnectionMessage()
        self.sendBroadcast(message)

    def sendConnectionAcceptance(self, receiver_address: Address):
        message = ConnectionAcceptanceMessage(self.node.leader)
        self.send(message, receiver_address)

    def sendConnectionEstablished(self, receiver_address: Address):
        message = ConnectionEstablishedMessage()
        self.send(message, receiver_address)

    # --------------------------------------------------------------------------------------------------------------
    def sendAliveMessage(self, receiver_address: Address):
        message = AliveMessage()
        self.send(message, receiver_address)

    def sendElectionMessage(self):
        for neighbor in self.node.neighbors:
            if neighbor > self.network.IP:
                message = ElectionMessage()
                receiver_address = Address((neighbor, self.network.PORT))
                self.send(message, receiver_address)

    def sendVictoryMessage(self):
        for neighbor in self.node.neighbors:
            message = VictoryMessage()
            receiver_address = Address((neighbor, self.network.PORT))
            self.send(message, receiver_address)

    # --------------------------------------------------------------------------------------------------------------
    def sendTaskRequestMessage(self, receiver_address: Address):
        message = TaskRequestMessage()
        self.send(message, receiver_address)

    def sendTaskMessage(self, receiver_address: Address):
        message = TaskMessage()
        self.send(message, receiver_address)

    def sendRequestAudioMessage(self, receiver_address: Address):
        message = RequestAudioMessage()
        self.send(message, receiver_address)

    def sendResultMessage(self, receiver_address: Address, task: id, result: str):
        message = ResultMessage(task, result)
        self.send(message, receiver_address)
