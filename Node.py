from Address import Address
from NetworkUtils import NetworkUtils


class Node:
    def __init__(self):
        self.nu = NetworkUtils(self)
        self.neighbors = set()
        self.leader = None

    def addNeighbor(self, neighbor: Address):
        self.neighbors.add(neighbor)
        if len(self.neighbors) >= 2:
            print("Minimum number of neighbors reached")
            if self.leader is None:
                print("I don't have a leader, initiating election")
