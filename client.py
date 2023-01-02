if __name__ == '__main__':
    import socket

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the address and port of the server
    server_address = ('192.168.56.115', 10000)
    print('Connecting to {}:{}'.format(*server_address))
    sock.connect(server_address)

    # Send the "Hello, World!" message
    sock.sendall(b'Hello, World!')

    # Receive the response from the server and print it
    response = sock.recv(16)
    print('Received: {!r}'.format(response))

    # Close the connection
    sock.close()
