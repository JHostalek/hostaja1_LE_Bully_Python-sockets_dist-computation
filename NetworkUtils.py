import socket
import threading
from queue import Queue

import Node
from Message import *


def parseIp() -> str:
    """
    Parse the IP address from the output of ifconfig
    Works on Linux only (requires bash ip -a call)
    :return: ip address as string (e.g. "192.168.56.xxx")
    """
    import re
    import subprocess
    output = subprocess.run(["ip", "a"], stdout=subprocess.PIPE).stdout.decode()
    address_pattern = r"inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    matches = re.findall(address_pattern, output)
    return matches[2]


class NetworkUtils:
    def __init__(self, node: Node):
        self.BROADCAST_PORT = 5555
        self.PORT = 5556
        self.MAX_CONNECTIONS = 10
        self.SOCKET_TIMEOUT = 0.5

        self.terminate: threading.Event = threading.Event()
        self.node = node
        self.ip = parseIp()
        self.TAG = self.ip + " - "

        self.neighborSocks = []
        self.sock = None
        self.initListeningSocket()

        self.broadcastAddress = Address((self.ip, self.BROADCAST_PORT))
        self.broadcastSock = None
        self.initBroadcast()
        self.broadcastRequestConnection()

        self.messageQueue = Queue()
        self.processMessageThread = threading.Thread(target=self.processMessages)
        self.processMessageThread.start()

    def processMessages(self):
        while not self.terminate.is_set():
            if not self.messageQueue.empty():
                message, address = self.messageQueue.get()
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

    def initBroadcast(self):
        self.broadcastSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcastSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broadcastSock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, 1)
        bind_address = ('192.168.56.255', self.BROADCAST_PORT)
        self.broadcastSock.settimeout(self.SOCKET_TIMEOUT)
        self.broadcastSock.bind(bind_address)
        receive_thread = threading.Thread(target=self.listenBroadcast)
        receive_thread.start()

    def listenBroadcast(self):
        while not self.terminate.is_set():
            try:
                data, address = self.broadcastSock.recvfrom(1024)
                address = Address(address)
                message = pickle.loads(data)
                if address != self.broadcastAddress:
                    if isinstance(message, RequestConnectionMessage):
                        print(f"{self.TAG}Received connection request from {address.id}")
                        self.handleConnectionRequest(address)
                    else:
                        print(f"Received unknown broadcast message: {message}")
            except socket.timeout:
                pass

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

    def initListeningSocket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip, self.PORT))
        self.sock.listen(self.MAX_CONNECTIONS)
        self.sock.settimeout(self.SOCKET_TIMEOUT)
        receive_thread = threading.Thread(target=self.listen)
        receive_thread.start()

    def listen(self):
        while not self.terminate.is_set():
            try:
                client, address = self.sock.accept()
                address = Address(address)
                receive_thread = threading.Thread(target=self.receive, args=(client, address))
                receive_thread.start()
            except socket.timeout:
                pass

    def receive(self, client, address: Address):
        while not self.terminate.is_set():
            try:
                message = client.recv(1024)
                if message:
                    message = pickle.loads(message)
                    print(f"{self.TAG}Received message from {address.id}: {message.message}")
                    self.messageQueue.put((message, address))
            except socket.timeout:
                pass

    def send(self, message: Message, address: Address):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(address.address)
        client.send(message.toBytes())
        client.close()
