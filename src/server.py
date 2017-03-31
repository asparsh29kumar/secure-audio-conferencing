import logging
from multiprocessing import Process, Queue
from include.queue import signals
from include.process import key_exchange_server as ke

logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s',
					datefmt='%m/%d/%Y %I:%M:%S %p',
					level=logging.DEBUG)

try:
	queue_key_exchanges = Queue()
	queue_key_exchanges_signaller = Queue()
	process_key_exchange_facilitator = Process(target=ke.handle_client_connections,
											   args=(queue_key_exchanges, queue_key_exchanges_signaller))
	process_key_exchange_facilitator.start()

	countdown = 5
	iterate_flag = True
	while iterate_flag:
		logging.debug("Waiting to receive data from <key_exchanges> queue")
		queue_data = queue_key_exchanges.get(block=True)
		assert queue_data == signals.SIG_CHECKPOINT
		countdown -= 1
		if countdown <= 0:
			iterate_flag = False

	logging.debug("Signalling process to end")
	queue_key_exchanges_signaller.put(signals.SIG_FINISH)
	process_key_exchange_facilitator.join()
	queue_key_exchanges_signaller.close()
	queue_key_exchanges.close()
	print "Exiting server"
except Exception as e:
	print "\nServer exception trace:\n" + e.message
	raise
