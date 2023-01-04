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
        print(self.TAG + "Sending broadcast message")
        receiver_address = (self.network.BROADCAST_IP, self.network.BROADCAST_PORT)
        self.network.broadcastSocket.sendto(message.toBytes(), receiver_address)
        print(self.TAG + "Sending broadcast message DONE")

    def send(self, message: Message, receiver_address: Address):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(self.TAG + "Sending " + str(message) + " to " + str(receiver_address))
        client.connect(receiver_address.address)
        client.send(message.toBytes())
        client.close()
        print(self.TAG + "Sending " + str(message) + " to " + str(receiver_address) + " DONE")

    # --------------------------------------------------------------------------------------------------------------
    def sendConnectionRequest(self):
        # BROADCAST CONNECTION REQUEST
        message = RequestConnectionMessage()
        print(self.TAG + "Putting into queue " + str(message) + " to " + str(self.network.BROADCAST_IP))
        self.sendBroadcast(message)
        print(self.TAG + "Putting into queue " + str(message) + " to " + str(self.network.BROADCAST_IP) + " DONE")

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
