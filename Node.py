import threading
import time

from Address import Address
from Message import ElectionMessage, VictoryMessage, AliveMessage
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

    def handleNewConnection(self, neighbor: Address):
        with self.neighbors_lock:
            self.neighbors.add(neighbor.ip)
        if len(self.neighbors) >= self.MINIMUM_NEIGHBORS:
            print("Minimum number of neighbors reached")
            if self.leader is None:
                print("I don't have a leader, initiating election")
                print(f'Neighbors: {self.neighbors}')
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
            # This node is the coordinator, send Victory message to the node that sent the Election message
            self.nu.send(VictoryMessage(), Address((address.ip, self.nu.PORT)))
        else:
            self.state = "ELECTION"
            self.bullyElection()

    def handleVictoryMessage(self, message, address):
        """
        Handles a Victory message
        """
        self.state = "FOLLOWER"
        self.leader = address.ip
        print(f"New leader: {self.leader}")

    def handleAliveMessage(self, message, address):
        """
        Handles an Alive message
        """
        self.state = "WAITING"
        print(f"Received Alive message from {address.ip}, waiting for victory message")

    def bullyElection(self):
        """
        Implementation of the Bully Algorithm
        """
        if len(self.neighbors) < self.MINIMUM_NEIGHBORS:
            print("Not enough neighbors to start election")
            return
        highest_id = self.findHighestID(self.neighbors)
        if self.nu.ip == highest_id:
            # Send Victory message to all other processes and become the coordinator
            self.sendVictoryMessage()
        else:
            # Broadcast Election message to all processes with higher IDs
            self.sendElectionMessage()
            # Wait for a period of time for an Answer message
            time.sleep(self.WAIT_TIME)
            # If no Answer message received, broadcast Victory message and become coordinator
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
        for neighbor in self.neighbors:
            if neighbor > self.nu.ip:
                self.nu.send(ElectionMessage(), Address((neighbor, self.nu.PORT)))

    def sendVictoryMessage(self):
        """
        Sends a Victory message to all other processes and becomes the coordinator
        """
        self.state = "COORDINATOR"
        self.leader = self.nu.ip
        print(f"New leader: {self.leader}")
        for neighbor in self.neighbors:
            self.nu.send(VictoryMessage(), Address((neighbor, self.nu.PORT)))

    def findHighestID(self, ips: set[str]) -> str:
        sorted_ips = sorted(list(ips))
        return sorted_ips[-1]
