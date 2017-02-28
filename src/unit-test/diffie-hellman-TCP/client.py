# An echo client
import socket
from random import randint

def powerxor(a,b,c):
	res = 1
	for i in range(b):
		res = (res*a)%c
	return res

def clientTCP_DHE(sock, s_addr, s_port):
	server = (s_addr,s_port)
	sock.connect(server)
	data = sock.recv(16)
	p = int(data)
	sock.send("1")
	data = sock.recv(16)
	a = int(data)
	sock.send("1")
	xb = randint(10,p)
	yb = powerxor(a,xb,p)
	data = sock.recv(16)
	sock.send(str(yb))
	ya = int(data)
	secret = powerxor(ya,yb,p)
	# print "Alpha : ",a
	# print "P :",p
	# print "XB :",xb
	# print "YB :",yb
	# print "YA :",ya
	# print "\n\n\nSECERET :",secret
	return secret

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s_addr = '127.0.0.1'
s_port = 12345
print(clientTCP_DHE(sock, s_addr, s_port))
sock.close()