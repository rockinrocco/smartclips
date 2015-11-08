import socket
from time import *
import sys

serv = socket.socket()

HOST=''

PORT = 15000
#ADDR = (HOST, PORT)
BUFSIZE = 4096

try:
	serv.bind((HOST, PORT))
	serv.listen(5)
	conn,addr = serv.accept()
except KeyboardInterrupt:
	print "Keyboard Interrupt"
	serv.close()
	exit(1)

try:
	for i in range(0,3100):
		data=conn.recv(4096)
		sys.stdout.flush()
		chunk = data.split()
		sys.stdout.write("):%s\n" % chunk[-1])
		sleep(0.03)
	
	conn.close()
	sleep(10)

except KeyboardInterrupt:
	conn.close()
	print "bye!"
except IndexError:
	conn.close()
	print "indexError"
