import socket
import threading


class NetworkUtils:
    def __init__(self):
        self.ip = self.parseIp()
        self.BROADCAST_PORT = 5555
        self.broadcastSock = self.initBroadcast()
        self.terminationEvent: threading.Event = threading.Event()

    def initBroadcast(self):
        # Create the socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, 1)

        # Set the IP and port to listen on
        # TODO: ALLOW LOCALHOST
        bind_address = ('192.168.56.255', self.BROADCAST_PORT)

        # Bind to the specific IP address and port
        sock.bind(bind_address)
        # Create threads for sending and receiving messages
        receive_thread = threading.Thread(target=self.listenBroadcast)
        receive_thread.start()
        return sock

    def listenBroadcast(self):
        while not self.terminationEvent.is_set():
            print('Listening for messages...')
            data, address = self.broadcastSock.recvfrom(1024)
            if address == (self.ip, self.BROADCAST_PORT): continue
            print(f'{self.ip} - Received message from {address} : {data}')

    def sendBroadcast(self, message:str):
        # TODO: ALLOW LOCALHOST
        self.broadcastSock.sendto(message.encode(), ('192.168.56.255', self.BROADCAST_PORT))

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

    def terminate(self):
        self.terminationEvent.set()
