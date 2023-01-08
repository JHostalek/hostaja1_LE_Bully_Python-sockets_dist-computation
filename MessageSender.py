import fcntl
import os
import socket
import sys
import termios
import threading
import time

import Network
from Address import Address
from Message import *


class MessageSender:
    def __init__(self, network: Network):
        self.network = network
        self.node = network.node
        self.TAG = self.network.IP + " - "
        self.terminate = threading.Event()

    def sendBroadcast(self, message: Message):
        self.node.logicalClock += 1
        message.logicalClock = self.node.logicalClock
        receiver_address = (self.network.BROADCAST_IP, self.network.BROADCAST_PORT)
        self.network.broadcastSocket.sendto(message.toBytes(), receiver_address)

    def wait_for_ctrl_e(self):
        fd = sys.stdin.fileno()
        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)
        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
        try:
            while True:
                try:
                    c = sys.stdin.read(1)
                    if c == "\x05":
                        return False
                    elif c == "":
                        pass
                    else:
                        return True
                except IOError:
                    pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

    def send(self, message: Message, receiver_address: Address):
        if self.node.hold_each_message:
            self.node.log.debug(f'Press any key to send {message.message} or Ctrl+E to escape manual sending')
            self.node.hold_each_message = self.wait_for_ctrl_e()
        time.sleep(self.node.message_delay)
        self.node.logicalClock += 1
        message.logicalClock = self.node.logicalClock
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(receiver_address.address)
        client.send(message.toBytes())
        client.close()

    # --------------------------------------------------------------------------------------------------------------
    def sendConnectionRequest(self):
        # BROADCAST CONNECTION REQUEST
        message = RequestConnectionMessage()
        self.sendBroadcast(message)

    def sendConnectionAcceptance(self, receiver_address: Address):
        message = ConnectionAcceptanceMessage(self.node.leader)
        try:
            self.send(message, receiver_address)
        except ConnectionError:
            self.node.log.debug(f'({self.node.logicalClock}) {self.TAG}SendConnectionAcceptance: ConnectionError to {str(receiver_address)}')
            self.node.removeNeighbor(receiver_address.ip)

    def sendConnectionEstablished(self, receiver_address: Address):
        message = ConnectionEstablishedMessage()
        try:
            self.send(message, receiver_address)
        except ConnectionError:
            self.node.log.debug(f'({self.node.logicalClock}) {self.TAG}SendConnectionEstablished: ConnectionError to {str(receiver_address)}')
            self.node.removeNeighbor(receiver_address.ip)

    # --------------------------------------------------------------------------------------------------------------
    def sendAliveMessage(self, receiver_address: Address):
        message = AliveMessage()
        try:
            self.send(message, receiver_address)
        except ConnectionError:
            self.node.log.debug(f'({self.node.logicalClock}) {self.TAG}SendAliveMessage: ConnectionError to {str(receiver_address)}')
            self.node.removeNeighbor(receiver_address.ip)

    def sendElectionMessage(self):
        with self.node.lock:
            for neighbor in self.node.neighbors:
                if neighbor > self.network.IP:
                    message = ElectionMessage()
                    receiver_address = Address((neighbor, self.network.PORT))
                    try:
                        self.send(message, receiver_address)
                    except ConnectionError:
                        self.node.log.debug(f'({self.node.logicalClock}) {self.TAG}SendElectionMessage: ConnectionError to {str(receiver_address)}')
                        self.node.log.debug(f'({self.node.logicalClock}) {self.TAG}Aborting election')
                        self.node.removeNeighbor(receiver_address.ip)
                        self.node.checkElection()
                        break

    def sendVictoryMessage(self):
        with self.node.lock:
            for neighbor in self.node.neighbors:
                message = VictoryMessage()
                receiver_address = Address((neighbor, self.network.PORT))
                try:
                    self.send(message, receiver_address)
                except ConnectionError:
                    self.node.log.debug(f'({self.node.logicalClock}) {self.TAG}SendVictoryMessage: ConnectionError to {str(receiver_address)}')
                    self.node.removeNeighbor(receiver_address.ip)
                    break

    # --------------------------------------------------------------------------------------------------------------
    def sendTaskRequestMessage(self, receiver_address: Address):
        message = TaskRequestMessage()
        try:
            if receiver_address.ip != self.network.IP:
                self.send(message, receiver_address)
        except ConnectionError:
            self.node.log.debug(f'({self.node.logicalClock}) {self.TAG}SendTaskRequestMessage: ConnectionError to {str(receiver_address)}')
            self.node.removeNeighbor(receiver_address.ip)

    def sendTaskMessage(self, receiver_address: Address, task: int):
        message = TaskMessage(task)
        try:
            self.send(message, receiver_address)
        except ConnectionError:
            self.node.log.debug(f'({self.node.logicalClock}) {self.TAG}SendTaskMessage: ConnectionError to {str(receiver_address)}')
            self.node.removeNeighbor(receiver_address.ip)

    def sendRequestAudioMessage(self, receiver_address: Address, task: int):
        message = RequestAudioMessage(task)
        try:
            self.send(message, receiver_address)
        except ConnectionError:
            self.node.log.debug(f'({self.node.logicalClock}) {self.TAG}SendRequestAudioMessage: ConnectionError to {str(receiver_address)}')
            self.node.removeNeighbor(receiver_address.ip)

    def sendResultMessage(self, receiver_address: Address, task: int, result: str):
        message = ResultMessage(task, result)
        try:
            self.send(message, receiver_address)
        except ConnectionError:
            self.node.log.debug(f'({self.node.logicalClock}) {self.TAG}SendResultMessage: ConnectionError to {str(receiver_address)}')
            self.node.removeNeighbor(receiver_address.ip)

    # --------------------------------------------------------------------------------------------------------------
    def sendCheckpointMessage(self, receiver_address: Address, checkpoint: [Task]):
        message = CheckpointMessage(checkpoint)
        try:
            self.send(message, receiver_address)
        except ConnectionError:
            self.node.log.debug(f'({self.node.logicalClock}) {self.TAG}SendCheckpointMessage: ConnectionError to {str(receiver_address)}')
            self.node.removeNeighbor(receiver_address.ip)

    def sendRequestCheckpointMessage(self, receiver_address: Address):
        message = RequestCheckpointMessage()
        try:
            self.send(message, receiver_address)
        except ConnectionError:
            self.node.log.debug(f'({self.node.logicalClock}) {self.TAG}SendRequestCheckpointMessage: ConnectionError to {str(receiver_address)}')
            self.node.removeNeighbor(receiver_address.ip)

    # --------------------------------------------------------------------------------------------------------------

    def sendTerminateMessage(self, receiver_address: Address):
        message = TerminateMessage()
        try:
            self.send(message, receiver_address)
        except ConnectionError:
            pass
            # self.node.log.debug(f'({self.node.logicalClock}) {self.TAG}SendTerminateMessage: ConnectionError to {str(receiver_address)}')
            # self.node.removeNeighbor(receiver_address.ip)
