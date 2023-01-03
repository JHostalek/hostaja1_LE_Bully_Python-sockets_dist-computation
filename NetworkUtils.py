import pickle
import socket
import threading

import Node
from Address import Address
from Message import RequestingConnection, TestMessage, AcceptingConnection


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

        self.terminate: threading.Event = threading.Event()
        self.node = node
        self.ip = parseIp()

        self.neighborSocks = []

        self.broadcastAddress = Address((self.ip, self.BROADCAST_PORT))
        self.broadcastSock = None
        self.initBroadcast()
        self.broadcastRequestConnection()

    def initBroadcast(self):
        self.broadcastSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcastSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broadcastSock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, 1)
        bind_address = ('192.168.56.255', self.BROADCAST_PORT)

        self.broadcastSock.bind(bind_address)
        receive_thread = threading.Thread(target=self.listenBroadcast)
        receive_thread.start()

    def listenBroadcast(self):
        while not self.terminate.is_set():
            data, address = self.broadcastSock.recvfrom(1024)
            address = Address(address)
            print(message)

            if address != self.broadcastAddress:
                message = pickle.loads(data)
                if isinstance(message, RequestingConnection):
                    print(f"{self.broadcastAddress} - Received connection request from {address}")
                    self.processConnectionRequest(address)
                elif isinstance(message, AcceptingConnection):
                    print(f"{self.broadcastAddress} - Received connection acceptance from {address}")
                    self.processConnectionAcceptance(address)
                else:
                    print(f"Received unknown broadcast message: {message}")

    def processConnectionRequest(self, sender: Address):
        self.node.neighbors.add(sender)
        self.sendAcceptingConnection(sender)

    def processConnectionAcceptance(self, address):
        self.node.neighbors.add(address)
        self.initSock(address)
        self.send(TestMessage(Address((self.ip, self.PORT)), address).toBytes(), address)

    def broadcastRequestConnection(self):
        self.broadcastSock.sendto(RequestingConnection().toBytes(), ('192.168.56.255', self.BROADCAST_PORT))

    def sendAcceptingConnection(self, address: Address):
        print(f"{self.broadcastAddress} - Sending connection acceptance to {address}")
        self.broadcastSock.sendto(AcceptingConnection().toBytes(), address.address)

    def initSock(self, address: Address):
        self.neighborSocks.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        self.neighborSocks[-1].bind(address.address)
        self.neighborSocks[-1].listen(self.MAX_CONNECTIONS)
        receive_thread = threading.Thread(target=self.listen, args=(self.neighborSocks[-1],))
        receive_thread.start()

    def listen(self, sock):
        while not self.terminate.is_set():
            client, address = sock.accept()
            address = Address(address)
            receive_thread = threading.Thread(target=self.receive, args=(client, address))
            receive_thread.start()

    def receive(self, client, address: Address):
        while not self.terminate.is_set():
            try:
                data = client.recv(1024)
                if data:
                    message: TestMessage = pickle.loads(data)
                    self.node.processMessage(message, address)
            except:
                pass

    def send(self, payload: bytes, address: Address):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f'DEBUG: {self.ip} - Sending message to {address}')
        client.connect(address.address)
        client.send(payload)
        client.close()
