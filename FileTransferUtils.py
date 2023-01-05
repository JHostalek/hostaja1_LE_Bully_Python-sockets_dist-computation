import socket


def sendFile(filename: str, ip: str, port: str):
    print("Sending file...")
    print("IP: " + ip + " Port: " + str(port) + " File: " + filename)
    # Create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the destination address
    destination_address = (ip, port)
    sock.connect(destination_address)

    with open(filename, 'rb') as file:
        # Read the file in chunks and send each chunk over the network
        chunk = file.read(1024)
        while chunk:
            sock.send(chunk)
            chunk = file.read(1024)

    # Close the file and the socket
    file.close()
    sock.close()


def startListeningForFile(ip: str, port: str):
    print("IP: " + ip + " Port: " + str(port))
    # Create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a local address
    local_address = (ip, port)
    sock.bind(local_address)

    # Listen for incoming connections
    sock.listen(1)
    return sock


def receiveFile(filename: str, sock: socket.socket):
    print("Receiving file...")
    print("As " + filename)

    # Accept an incoming connection
    connection, address = sock.accept()

    with open(filename, 'wb') as file:
        # Receive the file in chunks and write each chunk to the file
        chunk = connection.recv(1024)
        while chunk:
            file.write(chunk)
            chunk = connection.recv(1024)

    # Close the file and the socket
    file.close()
    connection.close()
    sock.close()
