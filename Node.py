import threading
import time

from Message import *
from NetworkUtils import NetworkUtils


class Node:
    def __init__(self):
        self.state = None
        self.nu = NetworkUtils(self)
        self.neighbors_lock = threading.Lock()
        self.neighbors = set()
        self.leader = None
        self.MINIMUM_NEIGHBORS = 2
        self.WAIT_TIME = 5

        self.TAG = self.nu.ip + " - "

    def handleNewConnection(self, message, address):
        if message is not None:
            self.leader = message.leader.ip
            print(f'{self.TAG}Established connection with {address}, leader is {self.leader}')
        else:
            print(f'{self.TAG}Established connection with {address}')
        with self.neighbors_lock:
            self.neighbors.add(address.ip)
        if self.leader is None and len(self.neighbors) >= self.MINIMUM_NEIGHBORS:
            print(f'{self.TAG}STARTING ELECTIONS - neighbors: {self.neighbors}')
            self.bullyElection()

    def handleElectionMessage(self, message, address):
        """
        Handles an Election message
        """
        if address.ip < self.nu.ip:
            self.sendAliveMessage(address)
        if self.state == "ELECTION":
            pass
        elif self.state == "COORDINATOR":
            self.nu.send(LeaderExistsMessage(), Address((address.ip, self.nu.PORT)))
        else:
            self.state = "ELECTION"
            self.bullyElection()

    def handleLeaderExistsMessage(self, message, address):
        self.state = "FOLLOWER"
        self.leader = address.ip
        print(f"{self.TAG}FOLLOWER, ALREADY EXISTING LEADER: {self.leader}")

    def handleVictoryMessage(self, message, address):
        """
        Handles a Victory message
        """
        self.state = "FOLLOWER"
        self.leader = address.ip
        print(f"{self.TAG}FOLLOWER, NEW LEADER IS: {self.leader}")

    def handleAliveMessage(self, message, address):
        """
        Handles an Alive message
        """
        self.state = "WAITING"

    def bullyElection(self):
        """
        Implementation of the Bully Algorithm
        """
        if len(self.neighbors) < self.MINIMUM_NEIGHBORS:
            print(f"{self.TAG}Not enough neighbors to start election")
            return
        self.sendElectionMessage()
        time.sleep(self.WAIT_TIME)
        if self.state == "ELECTION":
            self.sendVictoryMessage()

    def sendAliveMessage(self, address: Address):
        """
        Sends an Alive message to the node that sent the Election message
        """
        self.nu.send(AliveMessage(), Address((address.ip, self.nu.PORT)))

    def sendElectionMessage(self):
        """
        Sends an Election message to all processes with higher IDs
        """
        self.state = "ELECTION"
        with self.neighbors_lock:
            for neighbor in self.neighbors:
                if neighbor > self.nu.ip:
                    self.nu.send(ElectionMessage(), Address((neighbor, self.nu.PORT)))

    def sendVictoryMessage(self):
        """
        Sends a Victory message to all other processes and becomes the coordinator
        """
        self.state = "COORDINATOR"
        self.leader = self.nu.ip
        print(f"{self.TAG}I AM THE NEW LEADER")
        with self.neighbors_lock:
            for neighbor in self.neighbors:
                self.nu.send(VictoryMessage(), Address((neighbor, self.nu.PORT)))

    def findHighestID(self, ips: set[str]) -> str:
        sorted_ips = sorted(list(ips))
        return sorted_ips[-1]
