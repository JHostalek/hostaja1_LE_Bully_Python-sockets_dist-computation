from NetworkUtils import NetworkUtils


class Node:
    def __init__(self):
        self.nu = NetworkUtils()
        self.nu.sendBroadcast("Notifying other nodes of my existence")


