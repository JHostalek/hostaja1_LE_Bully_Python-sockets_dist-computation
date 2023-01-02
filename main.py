import socket
import struct
import time

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

import re
import subprocess

output = subprocess.run(["ip", "a"], stdout=subprocess.PIPE).stdout.decode()

address_pattern = r"inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"

matches = re.findall(address_pattern, output)

ip_address = matches[2]


# Set the IP and port to listen on
bind_address = ('192.168.56.255', 10000)

# Bind to the specific IP address and port
sock.bind(bind_address)

# Set timeout for socket to 1 second
sock.settimeout(20)
sock.sendto(b'Keepalive', ('192.168.56.255', 10000))
try:
    while True:
        print('Listening for messages...')
        data, address = sock.recvfrom(1024)
        print(f'Received message from {address} {ip_address}: {data}')
        if address == ip_address: continue
        time.sleep(5)
        sock.sendto(b'Keepalive', ('192.168.56.255', 10000))
except KeyboardInterrupt:
    print('Exiting...')
finally:
    sock.close()
