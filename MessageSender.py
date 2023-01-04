import queue
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
        self.broadcast_q = queue.Queue()
        self.q = queue.Queue()
        self.lock = threading.Lock()
        self.sendThread = None
        self.terminate = threading.Event()

    def start(self):
        self.sendThread = threading.Thread(target=self.sendMessages)
        self.sendThread.start()

    def stop(self):
        self.terminate.set()
        self.sendThread.join()

    def sendMessages(self):
        while not self.terminate.is_set():
            while not self.broadcast_q.empty():
                print(self.TAG + "Sending broadcast message")
                message = self.broadcast_q.get()
                receiver_address = (self.network.BROADCAST_IP, self.network.BROADCAST_PORT)
                self.network.broadcastSocket.sendto(message.toBytes(), receiver_address)
                print(self.TAG + "Sending broadcast message DONE")

            while not self.q.empty():
                message, address = self.q.get()
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print(self.TAG + "Sending " + str(message) + " to " + str(address))
                client.connect(address.address)
                client.send(message.toBytes())
                client.close()

    # --------------------------------------------------------------------------------------------------------------
    def sendConnectionRequest(self):
        # BROADCAST CONNECTION REQUEST
        message = RequestConnectionMessage()
        print(self.TAG + "Putting into queue " + str(message) + " to " + str(self.network.BROADCAST_IP))
        self.lock.acquire()
        self.broadcast_q.put(message)
        self.lock.release()
        print(self.TAG + "Putting into queue " + str(message) + " to " + str(self.network.BROADCAST_IP) + " DONE")

    def sendConnectionAcceptance(self, receiver_address: Address):
        message = ConnectionAcceptanceMessage(self.node.leader)
        self.lock.acquire()
        self.q.put((message, receiver_address))
        self.lock.release()

    def sendConnectionEstablished(self, receiver_address: Address):
        message = ConnectionEstablishedMessage()
        self.lock.acquire()
        self.q.put((message, receiver_address))
        self.lock.release()

    # --------------------------------------------------------------------------------------------------------------
    def sendAliveMessage(self, receiver_address: Address):
        message = AliveMessage()
        self.lock.acquire()
        self.q.put((message, receiver_address))
        self.lock.release()

    def sendElectionMessage(self):
        for neighbor in self.node.neighbors:
            if neighbor > self.network.IP:
                message = ElectionMessage()
                receiver_address = Address((neighbor, self.network.PORT))
                self.lock.acquire()
                self.q.put((message, receiver_address))
                self.lock.release()

    def sendVictoryMessage(self):
        for neighbor in self.node.neighbors:
            message = VictoryMessage()
            receiver_address = Address((neighbor, self.network.PORT))
            self.lock.acquire()
            self.q.put((message, receiver_address))
            self.lock.release()

    # --------------------------------------------------------------------------------------------------------------
