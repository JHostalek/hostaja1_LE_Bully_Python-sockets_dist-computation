import socket
import struct
import time
import threading

def receive_messages(sock):
    while True:
        print('Listening for messages...')
        data, address = sock.recvfrom(1024)
        if address[0] == ip_address: continue
        print(f'Received message from {address} {ip_address}: {data}')

def send_keepalive(sock, interval):
    while True:
        time.sleep(interval)
        sock.sendto(b'Keepalive', ('192.168.56.255', PORT))

def get_ip():
    import re
    import subprocess
    output = subprocess.run(["ip", "a"], stdout=subprocess.PIPE).stdout.decode()
    address_pattern = r"inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    matches = re.findall(address_pattern, output)
    return matches[2]

def main():
    # Create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, 1)

    global ip_address
    ip_address = get_ip()
    PORT = 5555
    # Set the IP and port to listen on
    bind_address = ('192.168.56.255', PORT)

    # Bind to the specific IP address and port
    sock.bind(bind_address)

    # Set timeout for socket to 1 second
    sock.settimeout(20)

    # Create threads for sending and receiving messages
    receive_thread = threading.Thread(target=receive_messages, args=(sock,))
    send_thread = threading.Thread(target=send_keepalive, args=(sock, 1))

    # Start threads
    receive_thread.start()
    send_thread.start()

    try:
        # Keep main thread alive until keyboard interrupt is received
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Exiting...')
    finally:
        sock.close()

if __name__ == '__main__':
    main()
