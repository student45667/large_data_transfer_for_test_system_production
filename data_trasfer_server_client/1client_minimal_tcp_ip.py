"""


# minimal client py
#!/usr/bin/env python3
import socket

s = socket.socket()
s.connect(('127.0.0.1', 5025))
s.send(b"*IDN?\n")
print(s.recv(1024))
s.close()



"""




# minimal VISA

#!/usr/bin/env python3
import pyvisa

rm = pyvisa.ResourceManager()
inst = rm.open_resource('TCPIP::raspi.local::5025::SOCKET')
inst.write_termination = '\n'
inst.read_termination = '\n'
response = inst.query('HOW ARE U')
print (response)
inst.close()

