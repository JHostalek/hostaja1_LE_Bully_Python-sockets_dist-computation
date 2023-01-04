import queue
import socket
import threading

import Network
from Address import Address
from Message import *


class MessageReceiver:
    def __init__(self, network: Network):
        self.network = network
        self.node = network.node
        self.broadcastSocket = self.network.broadcastSocket
        self.socket = self.network.socket

        self.TAG = self.network.IP + " - "

        self.connection_q = queue.Queue()
        self.election_q = queue.Queue()
        self.task_q = queue.Queue()

        self.listenThread = None
        self.broadcastThread = None
        self.terminate = threading.Event()

    def start(self):
        self.broadcastThread = threading.Thread(target=self.listenBroadcast)
        self.broadcastThread.start()
        self.listenThread = threading.Thread(target=self.listenForNewConnections)
        self.listenThread.start()

    def stop(self):
        self.terminate.set()
        self.broadcastThread.join()
        self.listenThread.join()
        self.socket.close()
        self.broadcastSocket.close()

    def listenBroadcast(self):
        while not self.terminate.is_set():
            try:
                data, address = self.broadcastSocket.recvfrom(1024)
                address = Address(address)
                message = pickle.loads(data)
                if address != Address((self.network.IP, self.network.BROADCAST_PORT)):
                    self.connection_q.put((message, address))
            except socket.timeout:
                pass

    def listenForNewConnections(self):
        while not self.terminate.is_set():
            try:
                client, address = self.socket.accept()
                address = Address(address)
                receive_thread = threading.Thread(target=self.listen, args=(client, address))
                receive_thread.start()
            except socket.timeout:
                pass

    def listen(self, client, address: Address):
        while not self.terminate.is_set():
            try:
                message = client.recv(1024)
                if message:
                    message = pickle.loads(message)
                    print(f"{self.TAG}Received message from {address.id}: {message.message}")
                    if message.category == "connection":
                        self.connection_q.put((message, address))
                    elif message.category == "election":
                        self.election_q.put((message, address))
                    elif message.category == "task":
                        self.task_q.put((message, address))
                    else:
                        print(f"{self.TAG}Received unknown message: {message}")
            except socket.timeout:
                pass

    def consume(self):
        while not self.connection_q.empty():
            print(f"{self.TAG}Consuming messages. Queue sizes: {self.connection_q.qsize()}, {self.election_q.qsize()}, {self.task_q.qsize()}")
            message, address = self.connection_q.get()
            if isinstance(message, RequestConnectionMessage):
                self.node.handleConnectionRequest(address)
            elif isinstance(message, ConnectionAcceptanceMessage):
                print(f"{self.TAG}Processed connection acceptance from {address.id}")
                self.node.handleConnectionAcceptance(message, address)
            elif isinstance(message, ConnectionEstablishedMessage):
                print(f"{self.TAG}Processed connection established from {address.id}")
                self.node.handleConnectionEstablished(address)
            else:
                print(f"{self.TAG}Processed unknown connection message: {message}")

        while not self.election_q.empty():
            print(f"{self.TAG}Consuming messages. Queue sizes: {self.connection_q.qsize()}, {self.election_q.qsize()}, {self.task_q.qsize()}")
            message, address = self.election_q.get()
            if isinstance(message, ElectionMessage):
                print(f"{self.TAG}Processed election message from {address.id}")
                self.node.handleElectionMessage(message, address)
            elif isinstance(message, VictoryMessage):
                print(f"{self.TAG}Processed victory message from {address.id}")
                self.node.handleVictoryMessage(message, address)
            elif isinstance(message, AliveMessage):
                print(f"{self.TAG}Processed alive message from {address.id}")
                self.node.handleAliveMessage(message, address)
            else:
                print(f"{self.TAG}Processed unknown election message: {message}")

