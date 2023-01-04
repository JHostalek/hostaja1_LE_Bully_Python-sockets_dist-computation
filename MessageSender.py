import queue
import threading

import Network


class MessageSender:
    def __init__(self, network: Network):
        self.network = network
        self.TAG = self.network.ip + " - "
        self.q = queue.Queue()
        self.terminate = threading.Event()

    def send(self, message: Message, address: Address):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(address.address)
        client.send(message.toBytes())
        client.close()

    def handleConnectionRequest(self, sender: Address):
        self.sendConnectionAcceptance(Address((sender.ip, self.PORT)))

    def handleConnectionEstablished(self, sender: Address, message=None):
        self.node.handleNewConnection(message, sender)

    def broadcastRequestConnection(self):
        self.broadcastSock.sendto(RequestConnectionMessage().toBytes(), ('192.168.56.255', self.BROADCAST_PORT))

    def sendConnectionAcceptance(self, address: Address):
        print(f"{self.TAG}Sending connection acceptance to {address.id}")
        self.send(AcceptConnectionMessage(), address)

    def sendConnectionEstablished(self, address):
        if self.node.leader is not None:
            print(f"{self.TAG}Sending connection established to {address.id}, with leader {self.node.leader}")
        else:
            print(f"{self.TAG}Sending connection established to {address.id}, without leader")
        self.send(ConnectionEstablishedMessage(Address((self.node.leader, self.PORT))), Address((address.ip, self.PORT)))
