import random
import socket
import threading

from Address import Address
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


class DataCenter:
    def __init__(self):
        self.IP = parseIp()
        self.DATACENTER_PORT = 5557
        self.PORT = 5556
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.IP, self.DATACENTER_PORT))
        self.socket.settimeout(0.1)
        self.socket.listen(10)

        self.TAG = self.IP + " - "
        self.terminate = threading.Event()

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
                    self.consume(message, address)
            except socket.timeout:
                pass
            except ConnectionError:
                print(f"{self.TAG}Connection to {address.id} closed")
                break

    def consume(self, message, address):
        if isinstance(message, RequestAudioMessage):
            print(f"{self.TAG}Received request for audio from {address.id}")
            receiver_address = Address((address.ip, self.PORT))
            thread = threading.Thread(target=self.sendAudio, args=(receiver_address,))
            thread.start()

    def sendAudio(self, receiver_address: Address):
        audio = ''.join([chr(random.randint(97, 122)) for _ in range(10)])
        message = AudioMessage(audio)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(receiver_address.address)
        client.send(message.toBytes())
        client.close()
        print(f"{self.TAG}Sent audio to {receiver_address.id}")
