import socket
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET,        # Internet
                     socket.SOCK_DGRAM)     # UDP
sock.bind((UDP_IP, UDP_PORT))

start = time.time()
total = 0
bits = 0
for x in range(10000):
    data, addr = sock.recvfrom(1024)        # buffer size is 1024 bytes
    total = time.time() - start
    bits += len(data) * 8

print("received message: %s" % data, ": data rate:", bits/total)
