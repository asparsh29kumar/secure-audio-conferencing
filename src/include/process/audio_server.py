import logging
from threading import Thread
from Queue import Queue
from thread.stream_audio import udp_receive_audio, mix_audio, multicast_send_audio
from thread.utils import save_audio
from ..queue import signals, utils
from ..config.audio import WAVE_OUTPUT_FILENAME__RECEIVER


# TODO Remove unnecesary standard queues
def handle_audio_receipt(queue, signal_queue):
	# queue parameter used for receiving participant count.
	# TODO We don't need to use the queue for this purpose any more. Or, do we?
	logging.debug("About to start handling audio receipt")
	queue__receive_audio = Queue()
	queue__receive_audio_signaller = Queue()
	queue__save_audio = Queue()
	queue__save_audio_signaller = Queue()
	queue__frames_to_play = Queue()
	queue__frames_to_save = Queue()

	queue__mix_audio = Queue()
	queue__mix_audio_signaller = Queue()

	queue__multicast_send_audio = Queue()
	queue__multicast_send_audio_signaller = Queue()

	dict_queue__incoming_frames = {}

	thread__receive_audio = Thread(target=udp_receive_audio,
								   args=(
									   queue__receive_audio, queue__receive_audio_signaller,
									   dict_queue__incoming_frames))
	thread__mix_audio = Thread(target=mix_audio,
							   args=(queue__mix_audio, queue__mix_audio_signaller, dict_queue__incoming_frames,
									 queue__frames_to_play, queue__frames_to_save))
	thread__multicast_send_audio = Thread(target=multicast_send_audio,
										  args=(queue__multicast_send_audio, queue__multicast_send_audio_signaller,
												queue__frames_to_play))
	thread__save_audio = Thread(target=save_audio,
								args=(queue__save_audio, queue__save_audio_signaller, WAVE_OUTPUT_FILENAME__RECEIVER,
									  queue__frames_to_save))
	thread__receive_audio.setDaemon(True)
	thread__mix_audio.setDaemon(True)
	thread__multicast_send_audio.setDaemon(True)
	thread__save_audio.setDaemon(True)
	thread__receive_audio.start()
	thread__mix_audio.start()
	thread__multicast_send_audio.start()
	thread__save_audio.start()
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH

	queue__receive_audio_signaller.put(signals.SIG_FINISH)
	queue__mix_audio_signaller.put(signals.SIG_FINISH)
	queue__multicast_send_audio_signaller.put(signals.SIG_FINISH)
	queue__save_audio_signaller.put(signals.SIG_FINISH)

	for queue in dict_queue__incoming_frames:
		utils.clear_queue(queue)
	dict_queue__incoming_frames.clear()
	utils.clear_queue(queue__frames_to_play)
	utils.clear_queue(queue__frames_to_save)
	utils.clear_queue(queue__receive_audio_signaller)
	utils.clear_queue(queue__mix_audio_signaller)
	utils.clear_queue(queue__multicast_send_audio_signaller)
	utils.clear_queue(queue__save_audio_signaller)
	utils.clear_queue(queue__receive_audio)
	utils.clear_queue(queue__mix_audio)
	utils.clear_queue(queue__multicast_send_audio)
	utils.clear_queue(queue__save_audio)

	queue__frames_to_play.join()
	queue__frames_to_save.join()

	queue__receive_audio_signaller.join()
	queue__mix_audio_signaller.join()
	queue__multicast_send_audio_signaller.join()
	queue__save_audio_signaller.join()

	queue__receive_audio.join()
	queue__mix_audio.join()
	queue__multicast_send_audio.join()
	queue__save_audio.join()

	thread__receive_audio.join()
	thread__mix_audio.join()
	thread__multicast_send_audio.join()
	thread__save_audio.join()
