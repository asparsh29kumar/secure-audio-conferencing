import logging
import socket

from ..config import server as server_config
from ..diffiehellman.transmission import client
from ..queue import signals, utils


def handle_server_connection(queue, signal_queue):
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket_address = server_config.SERVER_KEY_EXCHANGE__ADDRESS
	server_socket_port = server_config.SERVER_KEY_EXCHANGE__PORT
	# TODO Check if the socket is not None
	server = (server_socket_address, server_socket_port)
	client_socket.connect(server)

	logging.info(
		"Client IP address: " + str(client_socket.getsockname()[0]) + ":" + str(client_socket.getsockname()[1]))
	logging.info(
		"Server IP address: " + str(client_socket.getpeername()[0]) + ":" + str(client_socket.getpeername()[1]))

	while signal_queue.empty():
		secret_key = client.key_exchange(client_socket)
		queue.put(secret_key)
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	utils.clear_queue(signal_queue)
	client_socket.close()
