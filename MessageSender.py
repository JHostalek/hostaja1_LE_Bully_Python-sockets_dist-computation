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
        self.sockets = {}

    def sendBroadcast(self, message: Message):
        receiver_address = (self.network.BROADCAST_IP, self.network.BROADCAST_PORT)
        self.network.broadcastSocket.sendto(message.toBytes(), receiver_address)

    def send(self, message: Message, receiver_address: Address):
        if receiver_address not in self.sockets:
            self.sockets[receiver_address] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sockets[receiver_address].connect(receiver_address.address)
        self.sockets[receiver_address].send(message.toBytes())

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
