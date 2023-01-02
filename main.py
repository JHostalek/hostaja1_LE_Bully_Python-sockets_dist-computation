import socket
import struct

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set timeout for socket to 1 second
sock.settimeout(1)

# Set the IP and port to listen on
multicast_group = ('224.3.29.71', 10000)

# Bind to the multicast group and port
sock.bind(multicast_group)

# Tell the operating system to add the socket to the multicast group
# on all interfaces.
group = socket.inet_aton(multicast_group[0])
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# Listen for incoming connections
sock.listen()

# Receive messages
try:
    while True:
        print('Listening for incoming connections...')
        connection, address = sock.accept()
        print(f'Received connection from {address}')
        data = connection.recv(1024)
        print(f'Received message from {address}: {data}')
        connection.send(b'Hello, World!')
        connection.close()
except KeyboardInterrupt:
    print('Exiting...')
finally:
    # Leave the multicast group and close the socket
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
    sock.close()
