import socket

HOST = 'localhost'
PORT = 2121
FILENAME = 'ques.txt'

#TCP Server Code
def tcp_server():
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST,PORT))
        server_socket.listen()
        print("TCP Server listening for connections...")
        
        conn,addr=server_socket.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data=conn.recv(1024)
                if not data:
                    break
                print(f"Received: {data.decode()}")
                conn.sendall(b'ACK') #Send acknowledgment
    print("TCP Server closed.")
    
#TCP Client Code
def tcp_client():
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST,PORT))
        print("TCP Client connected to server.")
        
        with open(FILENAME,'r') as file:
            for line in file:
                client_socket.sendall(line.encode())
                data=client_socket.recv(1024)
                print(f"Server acknowledgment: {data.decode()}")
    print("TCP Client closed.")
    

#Main Function 
if __name__=="__main__":
    choice = input("Start as server(s) or client(c)? ")
    if choice.lower() == 's':
        tcp_server()
    elif choice.lower()== 'c':
        tcp_client()
    else:
        print("Invalid Input")