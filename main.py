import socket
import struct
import time

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
        print(f'Received message from {address}: {data}')
        time.sleep(5)
        sock.sendto(b'Keepalive', ('192.168.56.255', 10000))
except KeyboardInterrupt:
    print('Exiting...')
finally:
    sock.close()
