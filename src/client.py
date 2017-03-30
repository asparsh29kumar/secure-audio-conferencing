import socket
from include.diffiehellman.transmission import client, serversettings
import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

try:
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket_address = serversettings.SERVER_ADDRESS
	server_socket_port = serversettings.SERVER_PORT
	# TODO Check if the socket is not None
	server = (server_socket_address, server_socket_port)
	client_socket.connect(server)

	logging.info("Client IP address: " + str(client_socket.getsockname()[0]) + ":" + str(client_socket.getsockname()[1]))
	logging.info("Server IP address: " + str(client_socket.getpeername()[0]) + ":" + str(client_socket.getpeername()[1]))

	while True:
		shared_secret = client.key_exchange(client_socket)
		print "Calculated shared secret: " + str(shared_secret)

	client_socket.close()
except Exception as e:
	print "\nClient exception trace:\n" + e.message