import socket
import threading
import time

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
                    self.consume(message, address)
            except socket.timeout:
                pass
            time.sleep(0.5)

    def listenForNewConnections(self):
        while not self.terminate.is_set():
            try:
                client, address = self.socket.accept()
                address = Address(address)
                receive_thread = threading.Thread(target=self.listen, args=(client, address))
                receive_thread.start()
            except socket.timeout:
                pass
            time.sleep(0.5)

    def listen(self, client, address: Address):
        while not self.terminate.is_set():
            try:
                message = client.recv(1024)
                if message:
                    message = pickle.loads(message)
                    self.consume(message, address)
            except socket.timeout:
                pass
            time.sleep(0.5)

    def consume(self, message, address):
        if isinstance(message, RequestConnectionMessage):
            self.node.handleConnectionRequest(address)
        elif isinstance(message, ConnectionAcceptanceMessage):
            print(f"{self.TAG}Processed connection acceptance from {address.id}")
            self.node.handleConnectionAcceptance(message, address)
        elif isinstance(message, ConnectionEstablishedMessage):
            print(f"{self.TAG}Processed connection established from {address.id}")
            self.node.handleConnectionEstablished(address)
        elif isinstance(message, ElectionMessage):
            print(f"{self.TAG}Processed election message from {address.id}")
            self.node.handleElectionMessage(message, address)
        elif isinstance(message, VictoryMessage):
            print(f"{self.TAG}Processed victory message from {address.id}")
            self.node.handleVictoryMessage(message, address)
        elif isinstance(message, AliveMessage):
            print(f"{self.TAG}Processed alive message from {address.id}")
            self.node.handleAliveMessage(message, address)
        elif isinstance(message, TaskRequestMessage):
            print(f"{self.TAG}Processed task request message from {address.id}")
            self.node.handleTaskRequestMessage(message, address)
        elif isinstance(message, TaskMessage):
            print(f"{self.TAG}Processed task message from {address.id}")
            self.node.handleTaskMessage(message, address)
        elif isinstance(message, RequestAudioMessage):
            pass
        elif isinstance(message, AudioMessage):
            print(f"{self.TAG}Processed audio message from {address.id}")
            self.node.handleAudioMessage(message, address)
        elif isinstance(message, ResultMessage):
            print(f"{self.TAG}Processed result message from {address.id}")
            self.node.handleResultMessage(message, address)
        elif isinstance(message, TerminateMessage):
            print(f"{self.TAG}Processed terminate message from {address.id}")
            exit(0)
        elif isinstance(message, CheckpointMessage):
            print(f"{self.TAG}Processed checkpoint message from {address.id}")
            self.node.handleCheckpointMessage(message, address)
        else:
            print(f"{self.TAG}Processed unknown message: {message}")
