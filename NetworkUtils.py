import pickle
import socket
import threading

import Message
import Node
from Address import Address
from Message import RequestingConnection, TestMessage


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
        self.sock = None
        self.initListeningSocket()

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
            message = pickle.loads(data)

            print(message)

            if address != self.broadcastAddress:
                if isinstance(message, RequestingConnection):
                    print(f"{self.broadcastAddress} - Received connection request from {address}")
                    self.handleConnectionRequest(address)
                else:
                    print(f"Received unknown broadcast message: {message}")

    def handleConnectionRequest(self, sender: Address):
        self.node.neighbors.add(sender)
        print(f"{self.broadcastAddress} - Accepting connection from {sender}")
        print(f"{self.broadcastAddress} - {self.node.neighbors}")
        self.sendConnectionAcceptance(Address((sender.ip, self.PORT)))

    def broadcastRequestConnection(self):
        self.broadcastSock.sendto(RequestingConnection().toBytes(), ('192.168.56.255', self.BROADCAST_PORT))

    def sendConnectionAcceptance(self, address: Address):
        self.send(TestMessage("TCP DEBUG MESSAGE").toBytes(), address)

    def initListeningSocket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip, self.PORT))
        self.sock.listen(self.MAX_CONNECTIONS)
        print(f"Listening on {self.ip}:{self.PORT}")
        receive_thread = threading.Thread(target=self.listen)
        receive_thread.start()

    def listen(self):
        while not self.terminate.is_set():
            client, address = self.sock.accept()
            address = Address(address)
            print(f"{self.broadcastAddress} - Received connection from {address}")
            receive_thread = threading.Thread(target=self.receive, args=(client, address))
            receive_thread.start()

    def receive(self, client, address: Address):
        while not self.terminate.is_set():
            try:
                data = client.recv(1024)
                if data:
                    print(f"{self.broadcastAddress} - Received message from {address}")
            except:
                print(f"{self.broadcastAddress} - Connection to {address} lost")
                pass

    def send(self, message: Message, address: Address):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(address.address)
        client.send(message.toBytes())
        client.close()
