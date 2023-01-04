import queue
import socket
import threading

import Network
from Message import *
from Node import Node


class MessageReceiver:
    def __init__(self, network: Network, node: Node):
        self.network = network
        self.node = node
        self.broadcastSocket = self.network.broadcastSocket
        self.socket = self.network.socket

        self.TAG = self.network.ip + " - "
        self.q = queue.Queue()

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
                if address != Address((self.network.ip, self.network.BROADCAST_PORT)):
                    self.q.put((message, address))
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
                    self.q.put((message, address))
            except socket.timeout:
                pass

    def consume(self):
        message, address = self.q.get()
        if isinstance(message, ConnectionEstablishedMessage):
            print(f"{self.TAG}Processed connection established from {address.id}")
            self.handleConnectionEstablished(message=message, sender=address)
        elif isinstance(message, AcceptConnectionMessage):
            print(f"{self.TAG}Processed connection acceptance from {address.id}")
            self.sendConnectionEstablished(address)
            self.handleConnectionEstablished(address)
        elif isinstance(message, ElectionMessage):
            print(f"{self.TAG}Processed election message from {address.id}")
            self.node.handleElectionMessage(message, address)
        elif isinstance(message, VictoryMessage):
            print(f"{self.TAG}Processed victory message from {address.id}")
            self.node.handleVictoryMessage(message, address)
        elif isinstance(message, AliveMessage):
            print(f"{self.TAG}Processed alive message from {address.id}")
            self.node.handleAliveMessage(message, address)
        elif isinstance(message, LeaderExistsMessage):
            print(f"{self.TAG}Processed leader exists message from {address.id}")
            self.node.handleLeaderExistsMessage(message, address)
        else:
            print(f"{self.TAG}Processed unknown message: {message}")
