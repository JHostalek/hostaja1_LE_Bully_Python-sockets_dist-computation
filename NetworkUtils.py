import pickle
import socket
import threading

import Node
from Address import Address
from Message import NotifyAllMessage, TestMessage


class NetworkUtils:
    def __init__(self, node: Node):
        self.BROADCAST_PORT = 5555
        self.PORT = 5556
        self.MAX_CONNECTIONS = 10

        self.terminate: threading.Event = threading.Event()
        self.node = node
        self.ip = self.parseIp()

        self.sock = None
        self.initSock()
        self.Address = Address((self.ip, self.PORT))

        self.broadcastSock = None
        self.initBroadcast()
        self.broadcastAddress = Address((self.ip, self.BROADCAST_PORT))

    def initBroadcast(self):
        # Create the socket
        self.broadcastSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcastSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broadcastSock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, 1)

        # Set the IP and port to listen on
        # TODO: ALLOW LOCALHOST
        bind_address = ('192.168.56.255', self.BROADCAST_PORT)

        # Bind to the specific IP address and port
        self.broadcastSock.bind(bind_address)
        # Create threads for sending and receiving messages
        receive_thread = threading.Thread(target=self.listenBroadcast)
        receive_thread.start()

    def listenBroadcast(self):
        while not self.terminate.is_set():
            data, address = self.broadcastSock.recvfrom(1024)
            address = Address(address)
            # Ignore broadcast messages from self
            if address != self.broadcastAddress:
                message: NotifyAllMessage = pickle.loads(data)
                self.node.processBroadcast(message, address)

    def sendBroadcast(self, payload: bytes):
        # TODO: ALLOW LOCALHOST
        self.broadcastSock.sendto(payload, ('192.168.56.255', self.BROADCAST_PORT))

    def parseIp(self) -> str:
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

    def initSock(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip, self.PORT))
        self.sock.listen(self.MAX_CONNECTIONS)
        receive_thread = threading.Thread(target=self.listen)
        receive_thread.start()

    def listen(self):
        while not self.terminate.is_set():
            client, address = self.sock.accept()
            address = Address(address)
            receive_thread = threading.Thread(target=self.receive, args=(client, address,))
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
        print(f'DEBUG: {self.Address} - Sending message to {address}')
        client.connect(address.address)
        client.send(payload)
        client.close()
