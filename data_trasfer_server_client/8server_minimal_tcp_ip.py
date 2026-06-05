#!/usr/bin/env python3
import socket
import threading
import time
import os
import glob

ramdisk_path = "/mnt/dlog_ramdisk/"

#------------- Generating dummy data & file to send via TCP----------------------- 
timestr = time.strftime("%y%m%d_%H%M%S") # Convert to formatted string: yymmdd_hhmmss
datalog_dummy = b"X" * (1024*1024)  

dlog_filename = f"dlog_1{timestr}.log"
with open(dlog_filename, 'wb') as f:
    f.write(datalog_dummy)
    
dlog_filename = f"dlog_2{timestr}.log"    
with open(dlog_filename, 'wb') as f:
    f.write(datalog_dummy)
    
dlog_filename = f"dlog_3{timestr}.log"    
with open(dlog_filename, 'wb') as f:
    f.write(datalog_dummy)

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
         
         #------ scan for old dlog send delete if not found dummy mesage---
         search_pattern = f"{ramdisk_path}*.log"
         log_files = sorted(glob.glob(search_pattern))
         if log_files:
            log_file = log_files[0]  # oldest file first
            print(f"Sending {log_file}...")
            with open(log_file, 'rb') as f:
                log_file_data = f.read()
            sock.sendall(log_file_data + b"\n") 
            os.remove(log_file)
            print(f"sent and deleted {log_file}\n")
         else:
             # No files yet, wait and check again
             print("Waiting for logs...", end='\r')
             answer = "no new data found \n"
             sock.sendall( answer.encode() )  #convert string to bytes
        #----------------------------------------------------------
  
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




"""

# ============= Create 16 MB RAM drive ==================
sudo mkdir -p /mnt/ramdisk
sudo mount -t tmpfs -o size=16M tmpfs /mnt/ramdisk

# Verify it's created
df -h /mnt/ramdisk
mount | grep ramdisk

#============== Make it permament =====================
sudo nano /etc/fstab
Add this line at the end:
tmpfs           /mnt/ramdisk tmpfs   size=16M        0       0





"""