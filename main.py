import socket
import struct
import sys
import time

if __name__ == '__main__':
    message = socket.gethostname().encode('ascii')

    # Create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set a timeout so the socket does not block indefinitely when trying
    # to receive data.
    sock.settimeout(1)

    # Set the time-to-live for messages to 1 so they do not go past the
    # local network segment.
    ttl = struct.pack('b', 10)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    # Bind to the server address
    server_address = ('', 5555)
    sock.bind(server_address)

    multicast_group = ('224.3.29.71', 5555)

    # Tell the operating system to add the socket to the multicast group
    # on all interfaces.
    group = socket.inet_aton('224.3.29.71')
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # Receive/respond loop
    while True:
        try:
            print('\nWaiting to receive message')
            data, address = sock.recvfrom(1024)

            print(f'Received {len(data)} bytes from {address}')
            print(data)

            # print(f'Sending acknowledgement to {address}')
            # sock.sendto(b'ACK', address)
        except socket.timeout:
            print('Timed out, trying again')
            sock.sendto(message, multicast_group)
            continue
        except KeyboardInterrupt:
            print('Exiting program')
            break

    # Leave the multicast group
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
    sock.close()
