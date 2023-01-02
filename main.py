import socket
import struct
import sys
import time

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ip_address = sys.argv[1]

# Set the IP and port to listen on
bind_address = (ip_address, 10000)

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

while True:
    try:
        print('Listening for messages...')
        data, address = sock.recvfrom(1024)
        print(f'Received message from {address}: {data}')

        # Send a message to the multicast group every 5 seconds
        time.sleep(5)
        message = f'Keepalive from {bind_address}'
        sock.sendto(message, multicast_group)
    except KeyboardInterrupt:
        print('Exiting...')
        break
    except socket.timeout:
        print('Timed out waiting for a message')
        sock.sendto('Keepalive from {}'.format(bind_address).encode('utf-8'), multicast_group)



# Leave the multicast group and close the socket
sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
sock.close()