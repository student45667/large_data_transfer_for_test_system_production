import socket
import time

s = socket.socket()
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024*10)
s.connect(('raspi.local', 5025))

for i in range(5):
    start = time.time()
    s.send(b"GET_LOG?\n")
    data = s.recv(1024*1024 + 256)  # 1MB + header
    elapsed = time.time() - start
    print(f"[{i}] {elapsed*1000:.1f}ms for 1MB = {1/elapsed:.1f}MB/s")

s.close()
