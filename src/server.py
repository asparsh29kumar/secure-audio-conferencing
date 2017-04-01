import logging
from multiprocessing import Process, Queue
from include.queue import signals, utils as q_utils
from include.process import key_exchange_server as ke, audio_server

logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s',
					datefmt='%m/%d/%Y %I:%M:%S %p',
					level=logging.DEBUG)

try:
	queue__key_exchanges = Queue()
	queue__key_exchanges_signaller = Queue()
	queue__audio_receiver = Queue()
	queue__audio_receiver_signaller = Queue()
	process__key_exchange_facilitator = Process(target=ke.handle_client_connections,
												args=(queue__key_exchanges, queue__key_exchanges_signaller))
	process__audio_receiver = Process(target=audio_server.handle_audio_receipt,
									  args=(queue__audio_receiver, queue__audio_receiver_signaller))
	process__key_exchange_facilitator.start()
	process__audio_receiver.start()

	logging.debug("Status of process__key_exchange_facilitator: " + str(process__key_exchange_facilitator.is_alive()))
	logging.debug("Status of process__audio_receiver: " + str(process__audio_receiver.is_alive()))

	countdown = 5
	iterate_flag = True
	while iterate_flag:
		logging.debug("Waiting to receive data from <key_exchanges> queue")
		queue_data = queue__key_exchanges.get(block=True)
		assert queue_data == signals.SIG_CHECKPOINT
		countdown -= 1
		if countdown <= 0:
			iterate_flag = False

	logging.debug("Signalling process to end")
	queue__key_exchanges_signaller.put(signals.SIG_FINISH)
	queue__audio_receiver_signaller.put(signals.SIG_FINISH)
	process__key_exchange_facilitator.join()
	process__audio_receiver.join()
	q_utils.clear_queue(queue__key_exchanges)
	q_utils.clear_queue(queue__key_exchanges_signaller)
	q_utils.clear_queue(queue__audio_receiver)
	q_utils.clear_queue(queue__audio_receiver_signaller)
	queue__key_exchanges_signaller.close()
	queue__key_exchanges.close()
	queue__audio_receiver_signaller.close()
	queue__audio_receiver.close()
	print "Exiting server"
except Exception as e:
	print "\nServer exception trace:\n" + e.message
	raise
