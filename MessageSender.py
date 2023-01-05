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
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(receiver_address.address)
        client.send(message.toBytes())
        client.close()

    # --------------------------------------------------------------------------------------------------------------
    def sendConnectionRequest(self):
        # BROADCAST CONNECTION REQUEST
        message = RequestConnectionMessage()
        self.sendBroadcast(message)

    def sendConnectionAcceptance(self, receiver_address: Address):
        message = ConnectionAcceptanceMessage(self.node.leader)
        try:
            self.send(message, receiver_address)
        except ConnectionError:
            print(self.TAG + "SendConnectionAcceptance: ConnectionError to " + str(receiver_address))
            self.node.removeNeighbor(receiver_address.ip)

    def sendConnectionEstablished(self, receiver_address: Address):
        message = ConnectionEstablishedMessage()
        try:
            self.send(message, receiver_address)
        except ConnectionError:
            print(self.TAG + "SendConnectionEstablished: ConnectionError to " + str(receiver_address))
            self.node.removeNeighbor(receiver_address.ip)

    # --------------------------------------------------------------------------------------------------------------
    def sendAliveMessage(self, receiver_address: Address):
        message = AliveMessage()
        try:
            self.send(message, receiver_address)
        except ConnectionError:
            print(self.TAG + "SendAliveMessage: ConnectionError to " + str(receiver_address))
            self.node.removeNeighbor(receiver_address.ip)

    def sendElectionMessage(self):
        with self.node.lock:
            for neighbor in self.node.neighbors:
                if neighbor > self.network.IP:
                    message = ElectionMessage()
                    receiver_address = Address((neighbor, self.network.PORT))
                    try:
                        self.send(message, receiver_address)
                    except ConnectionError:
                        print(self.TAG + "SendElectionMessage: ConnectionError to " + str(receiver_address))
                        self.node.removeNeighbor(receiver_address.ip)
                        self.node.checkElection()
                        break

    def sendVictoryMessage(self):
        with self.node.lock:
            for neighbor in self.node.neighbors:
                message = VictoryMessage()
                receiver_address = Address((neighbor, self.network.PORT))
                try:
                    self.send(message, receiver_address)
                except ConnectionError:
                    print(self.TAG + "SendVictoryMessage: ConnectionError to " + str(receiver_address))
                    self.node.removeNeighbor(receiver_address.ip)
                    break

    # --------------------------------------------------------------------------------------------------------------
    def sendTaskRequestMessage(self, receiver_address: Address):
        message = TaskRequestMessage()
        try:
            self.send(message, receiver_address)
        except ConnectionError:
            print(self.TAG + "SendTaskRequestMessage: ConnectionError to " + str(receiver_address))
            self.node.removeNeighbor(receiver_address.ip)

    def sendTaskMessage(self, receiver_address: Address):
        message = TaskMessage()
        try:
            self.send(message, receiver_address)
        except ConnectionError:
            print(self.TAG + "SendTaskMessage: ConnectionError to " + str(receiver_address))
            self.node.removeNeighbor(receiver_address.ip)

    def sendRequestAudioMessage(self, receiver_address: Address):
        message = RequestAudioMessage()
        try:
            self.send(message, receiver_address)
        except ConnectionError:
            print(self.TAG + "SendRequestAudioMessage: ConnectionError to " + str(receiver_address))
            self.node.removeNeighbor(receiver_address.ip)

    def sendResultMessage(self, receiver_address: Address, task: id, result: str):
        message = ResultMessage(task, result)
        try:
            self.send(message, receiver_address)
        except ConnectionError:
            print(self.TAG + "SendResultMessage: ConnectionError to " + str(receiver_address))
            self.node.removeNeighbor(receiver_address.ip)
