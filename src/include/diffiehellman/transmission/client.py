from random import randint
from ...diffiehellman import utils as dhutils
import logging


# TCP implementation of Diffie-Hellman Key Exchange for client
def key_exchange(socket):
	try:
		data = socket.recv(dhutils.MAX_BUF_SIZE)
		assert data == dhutils.CMD_BEGIN, "Expected " + dhutils.CMD_BEGIN + " , received " + data
		socket.send(dhutils.CMD_ACK)
		logging.info("Received command to begin: %s", data)

		data = socket.recv(dhutils.MAX_BUF_SIZE)
		socket.send(dhutils.CMD_ACK)
		connection_list_size = int(data)
		logging.info("Received number of connections server is currently handling: %d", connection_list_size)

		data = socket.recv(dhutils.MAX_BUF_SIZE)
		socket.send(dhutils.CMD_ACK)
		dh_prime = int(data)
		logging.info("Received prime value: %d", dh_prime)

		data = socket.recv(dhutils.MAX_BUF_SIZE)
		socket.send(dhutils.CMD_ACK)
		dh_primitive_root = int(data)
		logging.info("Received primitive root: %d", dh_primitive_root)

		private_key = randint(dhutils.PRIVATE_KEY_MIN_VAL, dh_prime)
		logging.info("Generated private key: %d", private_key)

		secret = -1

		original_base = dh_primitive_root
		for i in range(connection_list_size - 1):
			data = socket.recv(dhutils.MAX_BUF_SIZE)
			logging.info("Received command to recycle (retrieve): %s", data)
			assert data == dhutils.CMD_RECYCLE_RETRIEVE, "Expected " + dhutils.CMD_RECYCLE_RETRIEVE + ", received " + data
			socket.send(dhutils.CMD_ACK)
			logging.debug("Sent acknowledgement: %s", dhutils.CMD_ACK)

			data = socket.recv(dhutils.MAX_BUF_SIZE)
			logging.info("Received command to request public key: %s", data)
			assert data == dhutils.CMD_REQ_PUBLIC_KEY, "Expected " + dhutils.CMD_REQ_PUBLIC_KEY + ", received " + data
			public_key = dhutils.exponent_with_modulo(original_base, private_key, dh_prime)
			socket.send(str(public_key))
			logging.info("Sent public key: %d", public_key)

			data = socket.recv(dhutils.MAX_BUF_SIZE)
			logging.info("Received command to recycle (reshare): %s", data)
			assert data == dhutils.CMD_RECYCLE_RESHARE, "Expected " + dhutils.CMD_RECYCLE_RESHARE + ", received " + data
			socket.send(dhutils.CMD_ACK)
			logging.debug("Sent acknowledgement: %s", dhutils.CMD_ACK)

			data = socket.recv(dhutils.MAX_BUF_SIZE)
			neighbor_public_key = int(data)
			logging.info("Received neighbor's public key: %d", neighbor_public_key)
			socket.send(dhutils.CMD_ACK)
			logging.debug("Sent acknowledgement: %s", dhutils.CMD_ACK)

			secret = dhutils.exponent_with_modulo(neighbor_public_key, private_key, dh_prime)
			logging.info("Calculated shared secret: %d", secret)

			original_base = neighbor_public_key
			logging.info("Updated original base to: %d", original_base)
		return secret
	except AssertionError as e:
		socket.send(dhutils.CMD_NACK)
		logging.debug("Sent no-acknowledgement: %s", dhutils.CMD_NACK)
		e.message += "\nCould not perform key exchange on this client"
		# logging.warning(e.message)
		raise
