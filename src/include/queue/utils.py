import Queue


def clear_queue(queue):
	while not queue.empty():
		try:
			queue.get(block=False)
		except Queue.Empty:
			continue
		# queue.task_done()
# It's risky to do task_done() because it isn't there in Queue.Queue(), but it is in multiprocessing.Queue().
