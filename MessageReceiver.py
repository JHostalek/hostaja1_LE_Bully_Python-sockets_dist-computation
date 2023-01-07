import socket
import threading
import time

import Network
from Address import Address
from Message import *


class MessageReceiver:
    def __init__(self, network: Network):
        self.MESSAGE_DELAY = 1
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
            time.sleep(self.MESSAGE_DELAY)
            try:
                data, address = self.broadcastSocket.recvfrom(1024)
                address = Address(address)
                message = pickle.loads(data)
                with self.node.clockLock:
                    self.node.logicalClock = max(self.node.logicalClock, message.logicalClock)
                if address != Address((self.network.IP, self.network.BROADCAST_PORT)):
                    self.consume(message, address)
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
            time.sleep(self.MESSAGE_DELAY)
            try:
                message = client.recv(16384)
                if message:
                    message = pickle.loads(message)
                    with self.node.clockLock:
                        self.node.logicalClock = max(self.node.logicalClock, message.logicalClock)
                    self.consume(message, address)
            except socket.timeout:
                pass

    def consume(self, message, address):
        if isinstance(message, RequestConnectionMessage):
            self.node.handleConnectionRequest(address)
        elif isinstance(message, ConnectionAcceptanceMessage):
            self.node.log.debug(f"({self.node.logicalClock}) {self.TAG}Processed connection acceptance from {address.id}")
            self.node.handleConnectionAcceptance(message, address)
        elif isinstance(message, ConnectionEstablishedMessage):
            self.node.log.debug(f"({self.node.logicalClock}) {self.TAG}Processed connection established from {address.id}")
            self.node.handleConnectionEstablished(address)
        elif isinstance(message, ElectionMessage):
            self.node.log.debug(f"({self.node.logicalClock}) {self.TAG}Processed election message from {address.id}")
            self.node.handleElectionMessage(message, address)
        elif isinstance(message, VictoryMessage):
            self.node.log.debug(f"({self.node.logicalClock}) {self.TAG}Processed victory message from {address.id}")
            self.node.handleVictoryMessage(message, address)
        elif isinstance(message, AliveMessage):
            self.node.log.debug(f"({self.node.logicalClock}) {self.TAG}Processed alive message from {address.id}")
            self.node.handleAliveMessage(message, address)
        elif isinstance(message, TaskRequestMessage):
            self.node.log.debug(f"({self.node.logicalClock}) {self.TAG}Processed task request message from {address.id}")
            self.node.handleTaskRequestMessage(message, address)
        elif isinstance(message, TaskMessage):
            self.node.log.debug(f"({self.node.logicalClock}) {self.TAG}Processed task message from {address.id}")
            self.node.handleTaskMessage(message, address)
        elif isinstance(message, RequestAudioMessage):
            pass
        elif isinstance(message, AudioMessage):
            self.node.log.debug(f"({self.node.logicalClock}) {self.TAG}Processed audio message from {address.id}")
            self.node.handleAudioMessage(message, address)
        elif isinstance(message, ResultMessage):
            self.node.log.debug(f"({self.node.logicalClock}) {self.TAG}Processed result message from {address.id}")
            self.node.handleResultMessage(message, address)
        elif isinstance(message, TerminateMessage):
            self.node.log.debug(f"({self.node.logicalClock}) {self.TAG}Processed terminate message from {address.id}")
            self.node.handleTerminateMessage(message, address)
        elif isinstance(message, CheckpointMessage):
            self.node.log.debug(f"({self.node.logicalClock}) {self.TAG}Processed checkpoint message from {address.id}")
            self.node.handleCheckpointMessage(message, address)
        else:
            self.node.log.debug(f"({self.node.logicalClock}) {self.TAG}Processed unknown message: {message}")
