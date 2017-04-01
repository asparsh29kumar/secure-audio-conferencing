import logging
import socket

from ..config import server as server_config
from ..diffiehellman.transmission import server
from ..queue import signals, utils


def handle_client_connections(queue, signal_queue):
	# TODO Check if the socket is not None
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_ip_address = server_config.SERVER_KEY_EXCHANGE__ADDRESS
	server_port = server_config.SERVER_KEY_EXCHANGE__PORT
	server_address = (server_ip_address, server_port)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind(server_address)
	server_socket.listen(server_config.MAX_NUMBER_OF_WAITING_CLIENTS)
	# TODO Make client_connections a queue?
	client_connections = []
	while signal_queue.empty():
		print "Waiting for connection..."
		[accepted_connection, accepted_address] = server_socket.accept()
		print "Accepted connection from address: " + str(accepted_address)
		logging.info("Accepted connection from address: " + str(accepted_address))
		client_connections.append(accepted_connection)
		client_connections = server.facilitate_key_exchange(client_connections)
		queue.put(signals.SIG_CHECKPOINT)
		queue.put((len(client_connections)))
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	for connection in client_connections:
		connection.close()
	utils.clear_queue(signal_queue)
	server_socket.close()
