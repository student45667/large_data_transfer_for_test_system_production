#!/usr/bin/env python3
import socket
import threading


def handle(sock, addr):
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    buf = ""
    while True:
        data = sock.recv(1024)
        if not data:
            break
        buf += data.decode()  # converts b'HOW ARE U\n' to 'HOW ARE U\n'
        
        while "\n" in buf:    # loops if \n still found in buff
            cmd, buf = buf.split("\n", 1)  # splits cmd once on \n:   buf=CMD1\nCMD2\nCMD3\n => cmd=CMD1  buf=CMD2\nCMD3\n
            if cmd.strip():                # if extracted cmd not empty, do something, send responce.
                # Some action here....
                print(f"RECIEVED {cmd}") 
                answer = f"RESPONSE to {cmd}\n"
                sock.sendall(answer.encode() )  #convert string to bytes

    sock.close()
    print("connection closed")        
          

        
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # ← add this first
server.bind(('0.0.0.0', 5025))
server.listen(5)

print("[*] Server running on 0.0.0.0:5025")

while True:
        sock, addr = server.accept()
        print(f"[CONNECT] {addr}")
        threading.Thread(target=handle, args=(sock, addr), daemon=True).start()
