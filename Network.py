import socket

import Node


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


class Network:
    def __init__(self, node: Node, data_center_ip='192.168.56.115', manual_ip=None):
        self.DATACENTER_IP = data_center_ip
        self.DATACENTER_PORT = 5557
        self.FILE_TRANSFER_PORT = 5558
        self.BROADCAST_IP = '192.168.56.255'
        self.BROADCAST_PORT = 5555
        self.IP = manual_ip if manual_ip is not None else parseIp()
        self.PORT = 5556
        self.SOCKET_TIMEOUT = 0.1
        self.MAX_CONNECTIONS = 10

        self.TAG = self.IP + " - "
        self.node = node

        self.socket, self.broadcastSocket = self.initSockets()
        # self.broadcastRequestConnection()

    def initSockets(self):
        self.node.log.debug(f"{self.TAG}Initializing sockets {self.IP}:{self.PORT}, {self.BROADCAST_IP}:{self.BROADCAST_PORT}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.IP, self.PORT))
        sock.settimeout(self.SOCKET_TIMEOUT)
        sock.listen(self.MAX_CONNECTIONS)

        broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, 1)
        broadcast_sock.settimeout(self.SOCKET_TIMEOUT)
        broadcast_sock.bind((self.BROADCAST_IP, self.BROADCAST_PORT))

        return sock, broadcast_sock
