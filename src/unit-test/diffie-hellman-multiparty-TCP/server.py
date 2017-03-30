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

def serverTCP_DHE(list_conn):
	p = get_next_prime(randint(50,700))
	a = find_primitive(p)
	for conn in list_conn:
		conn.send(str(p))
		data = conn.recv(16)
		if(int(data) == 1):
			conn.send(str(a))
		data = conn.recv(16)
		conn.send(str(len(list_conn)))
	size = len(list_conn)
	for i in range(size):
		for j in range(size):
			y = list_conn[j].recv(16)
			if(i == size-1):
				break
			if(j != (j+1)%size):
				list_conn[(j+1)%size].send(y)


		


list_of_client_conn = []


sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
port = 12345
ip_addr = '127.0.0.1'
server_address = (ip_addr,port)
sock.bind(server_address)
sock.listen(5)
while True:
	print "Waiting for connection"
	acceptedConn,addr = sock.accept()
	list_of_client_conn.append(acceptedConn)
	serverTCP_DHE(list_of_client_conn)
	acceptedConn.close()
sock.close()