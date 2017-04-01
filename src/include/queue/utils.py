import Queue


def clear_queue(queue):
	while not queue.empty():
		try:
			queue.get(block=False)
		except Queue.Empty:
			continue
		queue.task_done()
