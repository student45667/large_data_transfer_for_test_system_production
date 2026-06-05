
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
import time

timestr = time.strftime("%y%m%d_%H%M%S")


rm = pyvisa.ResourceManager()
inst = rm.open_resource('TCPIP::raspi.local::5025::SOCKET')
inst.write_termination = '\n'
inst.read_termination = '\n'
inst.timeout = 5000  # 1 seconds
inst.chunk_size = 8*1024*1024  # read 4MB chunks (if supported)
try:
	while True:
		time.sleep(0.25)
		response_simple_query = inst.query('IDN?')
		print (response_simple_query)
		
		response_heaher_of_dlog = inst.query('GET_LOG?') 
		print (f"recieved: {response_heaher_of_dlog}") 
		datalog = inst.read()
		print (f"recieved log size {len(datalog)}\n") 
		#------ append log dump from pi to file -----
		with open('dump_log.log', 'a') as f:  # append in bytes
			f.write(response_heaher_of_dlog + datalog ) #converted to bytes
		#------ append log dump from pi to file -----
		
except pyvisa.errors.VisaIOError as e:
    print(f"Timeout or error, not defined cmd: {e}")


inst.close()







