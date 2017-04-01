import logging
from multiprocessing import Process, Queue
from include.queue import signals, utils as q_utils
from include.process import key_exchange_client as ke, audio_client

logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s',
					datefmt='%m/%d/%Y %I:%M:%S %p',
					level=logging.DEBUG)

try:
	queue__key_exchange = Queue()
	queue__key_exchange_signaller = Queue()
	queue__audio_delivery = Queue()
	queue__audio_delivery_signaller = Queue()
	process__key_exchange = Process(target=ke.handle_server_connection,
									args=(queue__key_exchange, queue__key_exchange_signaller))
	process__audio_delivery = Process(target=audio_client.handle_audio_delivery,
									  args=(queue__audio_delivery, queue__audio_delivery_signaller))

	process__key_exchange.start()
	process__audio_delivery.start()

	logging.debug("Status of process__key_exchange: " + str(process__key_exchange.is_alive()))
	logging.debug("Status of process__audio_delivery: " + str(process__audio_delivery.is_alive()))

	countdown = 3
	iterate_flag = True
	while iterate_flag:
		logging.debug("Waiting to receive data from <key exchange> queue")
		shared_secret = queue__key_exchange.get(block=True)
		print "Calculated shared secret: " + str(shared_secret)
		countdown -= 1
		if countdown <= 0:
			iterate_flag = False

	logging.debug("Signalling process to end")
	queue__key_exchange_signaller.put(signals.SIG_FINISH)
	queue__audio_delivery_signaller.put(signals.SIG_FINISH)
	process__key_exchange.join()
	process__audio_delivery.join()
	q_utils.clear_queue(queue__key_exchange)
	q_utils.clear_queue(queue__key_exchange_signaller)
	q_utils.clear_queue(queue__audio_delivery)
	q_utils.clear_queue(queue__audio_delivery_signaller)
	queue__key_exchange_signaller.close()
	queue__key_exchange.close()
	queue__audio_delivery_signaller.close()
	queue__audio_delivery.close()
	print "Exiting client"
except Exception as e:
	print "\nClient exception trace:\n" + e.message
	raise
