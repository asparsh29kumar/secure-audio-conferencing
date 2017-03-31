import logging
import socket
from ..diffiehellman.transmission import server, serversettings
from ..queue import signals


def handle_client_connections(queue, signal_queue):
	# TODO Check if the socket is not None
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_ip_address = serversettings.SERVER_ADDRESS
	server_port = serversettings.SERVER_PORT
	server_address = (server_ip_address, server_port)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind(server_address)
	server_socket.listen(5)
	client_connections = []
	while signal_queue.empty():
		print "Waiting for connection..."
		[accepted_connection, accepted_address] = server_socket.accept()
		print "Accepted connection from address: " + str(accepted_address)
		logging.info("Accepted connection from address: " + str(accepted_address))
		client_connections.append(accepted_connection)
		queue.put(signals.SIG_CHECKPOINT)
		client_connections = server.facilitate_key_exchange(client_connections)
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	for connection in client_connections:
		connection.close()
	server_socket.close()
