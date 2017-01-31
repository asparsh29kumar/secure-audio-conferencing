# An echo client
import socket
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s_addr = '127.0.0.1'
s_port = 12345
server = (s_addr,s_port)
sock.connect(server)
print "Enter string to send :",
message = raw_input()
sock.sendall(message)
data = sock.recv(16)
print "Received :",data