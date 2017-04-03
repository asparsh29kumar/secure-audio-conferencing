from threading import Thread
from Queue import Queue
from thread.stream_audio import udp_send_audio, multicast_receive_audio, play_audio
from thread.utils import save_audio__old
from ..queue import signals, utils
from ..config.audio import WAVE_OUTPUT_FILENAME__SENDER
from time import sleep


def handle_audio_delivery(queue, signal_queue):
	queue__send_audio = Queue()
	queue__send_audio_signaller = Queue()
	queue__save_audio = Queue()
	queue__save_audio_signaller = Queue()
	queue__frames_to_save = Queue()
	queue__frames_to_play = Queue()

	queue__receive_audio = Queue()
	queue__receive_audio_signaller = Queue()
	queue__play_audio = Queue()
	queue__play_audio_signaller = Queue()

	# TODO Bug! When a client vanishes, the audio feed is bad.

	thread__record_and_send_audio = Thread(target=udp_send_audio,
										   args=(queue__send_audio, queue__send_audio_signaller, queue__frames_to_save))
	thread__save_audio = Thread(target=save_audio__old,
								args=(
									queue__save_audio, queue__save_audio_signaller, WAVE_OUTPUT_FILENAME__SENDER,
									queue__frames_to_save))

	thread__receive_audio = Thread(target=multicast_receive_audio,
								   args=(queue__receive_audio, queue__receive_audio_signaller, queue__frames_to_play))

	thread__play_audio = Thread(target=play_audio,
								args=(queue__play_audio, queue__play_audio_signaller, queue__frames_to_play))

	thread__record_and_send_audio.setDaemon(True)
	thread__save_audio.setDaemon(True)
	thread__receive_audio.setDaemon(True)
	thread__play_audio.setDaemon(True)
	thread__record_and_send_audio.start()
	thread__save_audio.start()
	thread__receive_audio.start()
	sleep(0.1)
	# Without this sleep, an error occurs:
	# python2.7: src/common/pa_front.c:196: InitializeHostApis: Assertion `hostApi->info.defaultInputDevice < hostApi->info.deviceCount' failed.
	thread__play_audio.start()
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	queue__send_audio_signaller.put(signals.SIG_FINISH)
	queue__save_audio_signaller.put(signals.SIG_FINISH)
	queue__receive_audio_signaller.put(signals.SIG_FINISH)
	queue__play_audio_signaller.put(signals.SIG_FINISH)

	utils.clear_queue(queue__save_audio)
	utils.clear_queue(queue__save_audio_signaller)
	utils.clear_queue(queue__send_audio)
	utils.clear_queue(queue__send_audio_signaller)
	utils.clear_queue(queue__frames_to_save)
	utils.clear_queue(queue__frames_to_play)
	utils.clear_queue(queue__receive_audio)
	utils.clear_queue(queue__receive_audio_signaller)
	utils.clear_queue(queue__play_audio)
	utils.clear_queue(queue__play_audio_signaller)

	queue__save_audio_signaller.join()
	queue__send_audio_signaller.join()
	queue__save_audio.join()
	queue__send_audio.join()
	queue__frames_to_save.join()
	queue__frames_to_play.join()
	queue__receive_audio.join()
	queue__receive_audio_signaller.join()
	queue__play_audio.join()
	queue__play_audio_signaller.join()

	thread__record_and_send_audio.join()
	thread__save_audio.join()
	thread__receive_audio.join()
	thread__play_audio.join()
