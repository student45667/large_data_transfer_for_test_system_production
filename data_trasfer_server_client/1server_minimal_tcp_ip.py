#!/usr/bin/env python3
import socket
import threading

def handle(sock, addr):
    data = sock.recv(1024)
    print(f"RECIEVED  {data} from {addr} \n")
    sock.sendall(b"HELLO FROM PI\n") 
    sock.close()
                
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # to reuse ports 
server.bind(('0.0.0.0', 5025))
server.listen(5)
print("[*] Server running on 0.0.0.0:5025")

while True:
        sock, addr = server.accept()
        threading.Thread(target=handle, args=(sock, addr), daemon=True).start()
