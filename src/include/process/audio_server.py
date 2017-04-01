import logging
import pyaudio
from threading import Thread
from Queue import Queue
from thread.stream_audio import udp_receive_audio, play_audio
from thread.utils import save_audio
from ..queue import signals, utils

# TODO Add these in a settings file.
FORMAT = pyaudio.paInt16
CHUNK = 1024
CHANNELS = 2
RATE = 44100
WAVE_OUTPUT_FILENAME = "serverFile.wav"


# TODO Remove unnecesary standard queues

def handle_audio_receipt(queue, signal_queue):
	logging.debug("About to start handling audio receipt")
	queue__receive_audio = Queue()
	queue__receive_audio_signaller = Queue()
	queue__play_audio = Queue()
	queue__play_audio_signaller = Queue()
	queue__save_audio = Queue()
	queue__save_audio_signaller = Queue()
	queue__frames_to_play = Queue()
	queue__frames_to_save = Queue()

	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

	thread__receive_audio = Thread(target=udp_receive_audio,
								   args=(queue__receive_audio, queue__receive_audio_signaller, CHUNK, CHANNELS,
										 queue__frames_to_play, queue__frames_to_save))
	thread__play_audio = Thread(target=play_audio,
								args=(
									queue__play_audio, queue__play_audio_signaller, stream, CHUNK,
									queue__frames_to_play))
	thread__save_audio = Thread(target=save_audio,
								args=(queue__save_audio, queue__save_audio_signaller, WAVE_OUTPUT_FILENAME, CHANNELS,
									  FORMAT, RATE, p, queue__frames_to_save))
	thread__receive_audio.setDaemon(True)
	thread__play_audio.setDaemon(True)
	thread__save_audio.setDaemon(True)
	thread__receive_audio.start()
	thread__play_audio.start()
	thread__save_audio.start()
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH

	queue__receive_audio_signaller.put(signals.SIG_FINISH)
	queue__play_audio_signaller.put(signals.SIG_FINISH)
	queue__save_audio_signaller.put(signals.SIG_FINISH)

	utils.clear_queue(queue__frames_to_play)
	utils.clear_queue(queue__frames_to_save)
	utils.clear_queue(queue__receive_audio_signaller)
	utils.clear_queue(queue__play_audio_signaller)
	utils.clear_queue(queue__save_audio_signaller)
	utils.clear_queue(queue__receive_audio)
	utils.clear_queue(queue__play_audio)
	utils.clear_queue(queue__save_audio)

	queue__frames_to_play.join()
	queue__frames_to_save.join()

	queue__receive_audio_signaller.join()
	queue__play_audio_signaller.join()
	queue__save_audio_signaller.join()

	queue__receive_audio.join()
	queue__play_audio.join()
	queue__save_audio.join()

	thread__receive_audio.join()
	thread__play_audio.join()
	thread__save_audio.join()
