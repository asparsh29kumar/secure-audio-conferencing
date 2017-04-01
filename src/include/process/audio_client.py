import pyaudio
from threading import Thread
from Queue import Queue
from thread.stream_audio import udp_send_audio
from thread.utils import save_audio
from ..queue import signals, utils

FORMAT = pyaudio.paInt16
CHUNK = 1024
CHANNELS = 2
RATE = 44100
WAVE_OUTPUT_FILENAME = "clientFile.wav"


def handle_audio_delivery(queue, signal_queue):
	queue__send_audio = Queue()
	queue__send_audio_signaller = Queue()
	queue__save_audio = Queue()
	queue__save_audio_signaller = Queue()
	queue__frames_to_save = Queue()

	p = pyaudio.PyAudio()

	audio_stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

	thread_send_audio = Thread(target=udp_send_audio,
							   args=(queue__send_audio, queue__send_audio_signaller, audio_stream, CHUNK,
									 queue__frames_to_save))
	thread_save_audio = Thread(target=save_audio,
							   args=(
								   queue__save_audio, queue__save_audio_signaller, WAVE_OUTPUT_FILENAME, CHANNELS,
								   FORMAT,
								   RATE, p, queue__frames_to_save))
	thread_send_audio.setDaemon(True)
	thread_save_audio.setDaemon(True)
	thread_send_audio.start()
	thread_save_audio.start()
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	queue__send_audio_signaller.put(signals.SIG_FINISH)
	queue__save_audio_signaller.put(signals.SIG_FINISH)

	utils.clear_queue(queue__save_audio)
	utils.clear_queue(queue__save_audio_signaller)
	utils.clear_queue(queue__send_audio)
	utils.clear_queue(queue__send_audio_signaller)
	utils.clear_queue(queue__frames_to_save)

	queue__save_audio_signaller.join()
	queue__send_audio_signaller.join()
	queue__save_audio.join()
	queue__send_audio.join()
	queue__frames_to_save.join()

	thread_send_audio.join()
	thread_save_audio.join()
