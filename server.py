if __name__ == '__main__':
    import socket

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the address and port
    server_address = ('192.168.56.15', 10000)
    print('Starting up on {}:{}'.format(*server_address))
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)

    # Accept a connection
    connection, client_address = sock.accept()
    print('Connection from {}:{}'.format(*client_address))

    # Receive data in chunks and echo it back
    while True:
        data = connection.recv(16)
        if data:
            print('Received {!r}'.format(data))
            connection.sendall(data)
        else:
            print('No more data from {}:{}'.format(*client_address))
            break

    # Close the connection
    connection.close()
