import socket
import struct
import time

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, 1)


def get_IP():
    import re
    import subprocess
    output = subprocess.run(["ip", "a"], stdout=subprocess.PIPE).stdout.decode()
    address_pattern = r"inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    matches = re.findall(address_pattern, output)
    return matches[2]


ip_address = get_IP()
PORT = 5555
# Set the IP and port to listen on
bind_address = ('192.168.56.255', PORT)

# Bind to the specific IP address and port
sock.bind(bind_address)

# Set timeout for socket to 1 second
sock.settimeout(20)
sock.sendto(b'Keepalive', ('192.168.56.255', PORT))
try:
    while True:
        print('Listening for messages...')
        data, address = sock.recvfrom(1024)
        if address[0] == ip_address: continue
        print(f'Received message from {address} {ip_address}: {data}')

        time.sleep(1)
        sock.sendto(b'Keepalive', ('192.168.56.255', PORT))
except KeyboardInterrupt:
    print('Exiting...')
finally:
    sock.close()
