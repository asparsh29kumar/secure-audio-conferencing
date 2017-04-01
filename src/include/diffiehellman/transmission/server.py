from random import randint
from ...diffiehellman import utils as dhutils
import logging


# TCP implementation of Diffie-Hellman Key Exchange for server
def facilitate_key_exchange(connection_list):
	try:
		dh_prime = dhutils.get_next_prime(randint(dhutils.PRIMES_LOWER_BOUND, dhutils.PRIMES_UPPER_BOUND))
		logging.info("Calculated prime value: %d", dh_prime)

		dh_primitive = dhutils.get_closest_primitive_root(dh_prime)
		logging.info("Calculated primitive root: %d", dh_primitive)

		connection_list_alive = []
		for connection in connection_list:
			try:
				connection.send(dhutils.CMD_HELLO)
				logging.info("Sent hello command: %s", dhutils.CMD_HELLO)
				data = connection.recv(dhutils.MAX_BUF_SIZE)
				logging.debug("Received acknowledgement: %s", data)
				if len(str(data)) == 0:
					continue
				assert data == dhutils.CMD_ACK, "Bad acknowledgement for " + dhutils.CMD_HELLO
				connection_list_alive.append(connection)
			except Exception as e:
				logging.info("Ignore presumed connection with exception: %s", e.message)

		connection_list = connection_list_alive
		for connection in connection_list:
			connection.send(dhutils.CMD_BEGIN)
			logging.info("Sent begin command: %s", dhutils.CMD_BEGIN)
			data = connection.recv(dhutils.MAX_BUF_SIZE)
			logging.debug("Received acknowledgement: %s", data)
			assert data == dhutils.CMD_ACK, "Bad acknowledgement for " + dhutils.CMD_BEGIN

			connection.send(str(len(connection_list)))
			logging.info("Sent number of connections server is currently handling: %d", len(connection_list))
			data = connection.recv(dhutils.MAX_BUF_SIZE)
			logging.debug("Received acknowledgement: %s", data)
			assert data == dhutils.CMD_ACK, "Bad acknowledgement for sending connection_list length"

			connection.send(str(dh_prime))
			logging.info("Sent prime value: %d", dh_prime)
			data = connection.recv(dhutils.MAX_BUF_SIZE)
			logging.debug("Received acknowledgement: %s", data)
			assert data == dhutils.CMD_ACK, "Bad acknowledgement for sending prime"

			connection.send(str(dh_primitive))
			logging.info("Sent primitive root: %d", dh_primitive)
			data = connection.recv(dhutils.MAX_BUF_SIZE)
			logging.debug("Received acknowledgement: %s", data)
			assert data == dhutils.CMD_ACK, "Bad acknowledgement for sending primitive"

		size = len(connection_list)

		for i in range(size - 1):
			logging.info("Entered recycle round: %d", i)
			public_keys = []
			for j in range(size):
				logging.info("Retrieving from client number: %d at %s:%s", j, str(connection_list[j].getpeername()[0]), str(connection_list[j].getpeername()[1]))
				connection_list[j].send(dhutils.CMD_RECYCLE_RETRIEVE)
				logging.info("Sent recycle (retrieve) command: %s", dhutils.CMD_RECYCLE_RETRIEVE)
				data = connection_list[j].recv(dhutils.MAX_BUF_SIZE)
				logging.debug("Received acknowledgement: %s", data)
				assert data == dhutils.CMD_ACK, "Bad acknowledgement for " + dhutils.CMD_RECYCLE_RETRIEVE

				connection_list[j].send(dhutils.CMD_REQ_PUBLIC_KEY)
				logging.info("Sent request public key command: %s", dhutils.CMD_REQ_PUBLIC_KEY)
				data = connection_list[j].recv(dhutils.MAX_BUF_SIZE)
				public_key = int(data)
				public_keys.append(public_key)
				logging.info("Received public key of client number %d: %d", j, public_key)

			for j in range(size):
				neighbor_index = (j + 1) % size
				if j == neighbor_index:
					break

				logging.info("Resharing with client number: %d at %s:%s", j, str(connection_list[neighbor_index].getpeername()[0]), str(connection_list[neighbor_index].getpeername()[1]))
				connection_list[neighbor_index].send(dhutils.CMD_RECYCLE_RESHARE)
				logging.info("Sent recycle command: %s", dhutils.CMD_RECYCLE_RESHARE)
				data = connection_list[neighbor_index].recv(dhutils.MAX_BUF_SIZE)
				logging.debug("Received acknowledgement: %s", data)
				assert data == dhutils.CMD_ACK, "Bad acknowledgement for " + dhutils.CMD_RECYCLE_RESHARE

				connection_list[neighbor_index].send(str(public_keys[j]))
				logging.info("Sent public key to neighbor process id: %d", neighbor_index)
				data = connection_list[neighbor_index].recv(dhutils.MAX_BUF_SIZE)
				logging.debug("Received acknowledgement: %s", data)
				assert data == dhutils.CMD_ACK, "Bad acknowledgement for sending a"
		return connection_list
	except AssertionError as e:
		e.message += "\nCould not facilitate key exchange on the server"
		# logging.warning(e.message)
		raise
