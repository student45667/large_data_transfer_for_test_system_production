#!/usr/bin/env python3
import socket
import threading
import time

#------------- Generating dummy data to send via TCP----------------------- 
datalog_dummy = b"X" * (1024*1024)
print(f"Generating datalog data of {(len(datalog_dummy))/(1024*1024)} Mbytes")  
#--------------------------------------------------------------------------


#------------------ TCP COMMUNICATION HANDLER------------------------------
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
                #------------------------------
                print(f"RECIEVED {cmd}") 
                # cmd interpereter called here
                command_handler(cmd)
                #------------------------------
    sock.close()
    print("connection closed")        
#--------------------------------------------------------------------------          



#--------------COMMANDS HANDLER ------------------------------------------- 
# add commands here 
def command_handler (cmd):
     timestr = time.strftime("%y%m%d_%H%M%S") # Convert to formatted string: yymmdd_hhmmss
    
     if cmd == "IDN?":
         answer = f"RESPONSE to {cmd} - I am PI  time:{timestr}\n"
         sock.sendall(answer.encode() )  #convert string to bytes
     if cmd == "GET_LOG?":
         answer =f"SENDING DATALOG  time:{timestr}\n" 
         sock.sendall( answer.encode() )  #convert string to bytes  
         sock.sendall(datalog_dummy + b"\n")  # already in bytes, adding end of cmd/data
#-------------------------------------------------------------------------- 


         

#------------------SET SOCKET TO LISTEN TO CLIENT -------------------------- 
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # ← add this first
server.bind(('0.0.0.0', 5025))
server.listen(5)
print("[*] Server running on 0.0.0.0:5025")
#--------------------------------------------------------------------------   



#------------------ CLIENT CONNECTED, SET A THREAD -------------------------- 
while True:
        sock, addr = server.accept() # NO client ?  script will wait here !!!!
        print(f"[CONNECT] {addr}")
        threading.Thread(target=handle, args=(sock, addr), daemon=True).start()
#-----------------------------------------------------------------------------


