import socket
import struct
import time

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set the IP and port to listen on
bind_address = ('192.168.56.1', 10000)

# Bind to the specific IP address and port
sock.bind(bind_address)

# Set timeout for socket to 1 second
sock.settimeout(1)

# Tell the operating system to add the socket to the multicast group
# on all interfaces.
multicast_group = ('224.3.29.71', 10000)
group = socket.inet_aton(multicast_group[0])
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# Receive messages
try:
    while True:
        print('Listening for messages...')
        data, address = sock.recvfrom(1024)
        print(f'Received message from {address}: {data}')

        # Send a message to the multicast group every 5 seconds
        time.sleep(5)
        message = f'Keepalive from {bind_address}'
        sock.sendto(message, multicast_group)
except KeyboardInterrupt:
    print('Exiting...')
finally:
    # Leave the multicast group and close the socket
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
    sock.close()
