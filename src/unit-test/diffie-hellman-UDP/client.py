# An echo client
import socket
from random import randint

def powerxor(a,b,c):
	res = 1
	for i in range(b):
		res = (res*a)%c
	return res

def clientTCP_DHE(sock, server_address):
	sock.sendto("1",server_address)
	data,_ = sock.recvfrom(16)
	p = int(data)
	sock.sendto("1",server_address)
	data = sock.recv(16)
	a = int(data)
	sock.sendto("1",server_address)
	xb = randint(10,p)
	yb = powerxor(a,xb,p)
	data = sock.recv(16)
	sock.sendto(str(yb),server_address)
	ya = int(data)
	secret = powerxor(ya,yb,p)
	return secret

s_port = 12345
s_ip_addr = '127.0.0.1'
cl_port = 12346
cl_ip_addr = '127.0.0.1'
server_address = (s_ip_addr,s_port)
client_address = (cl_ip_addr,cl_port)
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind(client_address)
print "SECRET :",(clientTCP_DHE(sock, server_address))