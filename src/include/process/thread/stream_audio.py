import logging
import socket
from ...queue import signals
from ...encrypt import utils


def udp_send_audio(queue, signal_queue, stream, chunk_size, queue__frames_to_save=None):
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	while signal_queue.empty():
		audio_data_clear = stream.read(chunk_size)
		audio_data_encrypted = utils.sxor(audio_data_clear)
		if queue__frames_to_save is not None:
			queue__frames_to_save.put(audio_data_clear)
		udp.sendto(audio_data_encrypted, ("127.0.0.1", 12344))
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	udp.close()


def udp_receive_audio(queue, signal_queue, chunk_size, channels, queue__frames_to_play, queue__frames_to_save=None):
	logging.debug("About to start streaming UDP")
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# TODO Make these addresses a part of serversettings.py
	# TODO Move serversettings.py to general include/ directory
	udp.bind(("127.0.0.1", 12344))
	while signal_queue.empty():
		sound_data, addr = udp.recvfrom(chunk_size * channels * 2)
		if queue__frames_to_play is not None:
			queue__frames_to_play.put(sound_data)
		if queue__frames_to_save is not None:
			queue__frames_to_save.put(sound_data)
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	udp.close()


def play_audio(queue, signal_queue, stream, chunk_size, queue__frames_to_play):
	buffer_size = 10
	logging.debug("About to start playing audio")
	while signal_queue.empty():
		# TODO Change == to >=
		if queue__frames_to_play.qsize() == buffer_size:
			while signal_queue.empty():
				alpha = queue__frames_to_play.get(block=True)
				stream.write(utils.sxor(alpha), chunk_size)
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	q_utils.clear_queue(queue__frames_to_play)
