import logging
from multiprocessing import Process, Queue
from include.queue import signals
from include.process import key_exchange_client as ke

logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s',
					datefmt='%m/%d/%Y %I:%M:%S %p',
					level=logging.DEBUG)

try:
	queue_key_exchange = Queue()
	queue_key_exchange_signaller = Queue()
	process_key_exchange = Process(target=ke.handle_server_connection,
								   args=(queue_key_exchange, queue_key_exchange_signaller))
	process_key_exchange.start()

	countdown = 3
	iterate_flag = True
	while iterate_flag:
		logging.debug("Waiting to receive data from <key exchange> queue")
		shared_secret = queue_key_exchange.get(block=True)
		print "Calculated shared secret: " + str(shared_secret)
		countdown -= 1
		if countdown <= 0:
			iterate_flag = False

	logging.debug("Signalling process to end")
	queue_key_exchange_signaller.put(signals.SIG_FINISH)
	process_key_exchange.join()
	queue_key_exchange_signaller.close()
	queue_key_exchange.close()
	print "Exiting client"
except Exception as e:
	print "\nClient exception trace:\n" + e.message
	raise
