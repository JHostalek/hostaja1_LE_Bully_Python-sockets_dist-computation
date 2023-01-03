import pickle
import socket
import threading

import Node
from Message import NotifyAllMessage


class NetworkUtils:
    def __init__(self, node: Node):
        self.terminate: threading.Event = threading.Event()
        self.node = node
        self.ip = self.parseIp()
        self.BROADCAST_PORT = 5555
        self.broadcastSock = None
        self.initBroadcast()

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
            if address == (self.ip, self.BROADCAST_PORT): continue
            message: NotifyAllMessage = pickle.loads(data)
            self.node.processBroadcast(message)

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
