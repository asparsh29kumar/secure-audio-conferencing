import socket
from include.diffiehellman.transmission import server, serversettings
import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

client_connections = []
try:
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_ip_address = serversettings.SERVER_ADDRESS
	server_port = serversettings.SERVER_PORT
	server_address = (server_ip_address, server_port)
	server_socket.bind(server_address)
	server_socket.listen(5)
	# TODO Check if the socket is not None
	while True:
		print "Waiting for connection..."
		accepted_connection, accepted_address = server_socket.accept()
		print "Accepted connection from address: " + str(accepted_address)
		client_connections.append(accepted_connection)

		server.facilitate_key_exchange(client_connections)

	for connection in client_connections:
		connection.close()
	server_socket.close()
except Exception as e:
	print "\nServer exception trace:\n" + e.message
	raise

# TODO Add heartbeat thread to reduce client_connections when client is killed.