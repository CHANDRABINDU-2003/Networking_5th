import socket
import time

HOST='localhost'
PORT=9999
BUFFER_SIZE=10000

client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
filename=input("Enter filename")

output_file=f"streaming_{filename}"
client.sendto(filename.encode(),(HOST,PORT))

response, _ =client.recvfrom(1024)
if response != b'OK':
    print("file not found on server")
    exit()

    