# A simple echo server
import socket
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
port = 12345
ip_addr = '127.0.0.1'
server_address = (ip_addr,port)
sock.bind(server_address)
sock.listen(5)
while(True):
	print "Waiting for connection"
	conn,cl_addr = sock.accept()
	data = conn.recv(16)
	print "Received :",data
	conn.sendall(data)
conn.close()