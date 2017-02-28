# A simple echo server
import socket
from random import randint

def isprime(a):
	i = 2
	while(i*i<=a):
		if(a%i == 0):
			return 0
		i+=1
	return 1

def powerxor(a,b,c):
	res = 1
	for i in range(b):
		res = (res*a)%c
	return res

def prime_factors(a):
    primfac = []
    d = 2
    while d*d <= a:
    	if(a%d == 0):
    		primfac.append(d)
        while (a % d) == 0:
            a //= d
        d += 1
    if a > 1:
       primfac.append(a)
    return primfac

def get_next_prime(a):
	if(a%2 == 0):
		a+=1
	while(isprime(a) == 0):
		a+=2
	return a

def check_primitive(parr,a,p):
	for i in parr:
		if(powerxor(a,(p-1)/i,p) == 1):
			return 0
	return 1

def find_primitive(p):
	m = p-1
	i = p-2
	parr = prime_factors(m)
	while(check_primitive(parr,i,p) != 1):
		i-=1
	return i

def get_next_prime(a):
	if(a%2 == 0):
		a+=1
	while (isprime(a)!=1):
		a+=2
	return a

def serverTCP_DHE(conn, client_address):
	p = get_next_prime(randint(100,1000))
	a = find_primitive(p)
	data,_ = conn.recvfrom(16)
	conn.sendto(str(p),client_address)
	data,_ = conn.recvfrom(16)
	if(int(data) == 1):
		conn.sendto(str(a),client_address)
	data,_ = conn.recvfrom(16)
	xa = randint(10,p)
	ya = powerxor(a,xa,p)
	if(int(data) == 1):
		conn.sendto(str(ya),client_address)
	data,_ = conn.recvfrom(16)
	yb = int(data)
	secret = powerxor(ya,yb,p)
	return secret

s_port = 12345
s_ip_addr = '127.0.0.1'
cl_port = 12346
cl_ip_addr = '127.0.0.1'
server_address = (s_ip_addr,s_port)
client_address = (cl_ip_addr,cl_port)
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind(server_address)
print "SECRET :",serverTCP_DHE(sock,client_address)
