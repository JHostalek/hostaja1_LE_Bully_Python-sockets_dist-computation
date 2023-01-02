import time

from NetworkUtils import NetworkUtils


class Node:
    def __init__(self):
        self.nu = NetworkUtils()
        self.nu.sendBroadcast("Notifying other nodes of my existence")
        self.send_keep_alive()

    def send_keep_alive(self):
        try:
            while True:
                time.sleep(1)
                self.nu.sendBroadcast("Keep alive")
        except KeyboardInterrupt:
            self.nu.terminate.set()
