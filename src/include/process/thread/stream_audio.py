import logging
import socket
import pyaudio
from Queue import Queue
# import numpy
from ...config import server as server_config, audio as audio_config
from ...encrypt import utils
from ...queue import signals, utils as q_utils


def udp_send_audio(queue, signal_queue, queue__frames_to_save=None):
	p = pyaudio.PyAudio()
	audio_stream = p.open(format=audio_config.FORMAT, channels=audio_config.CHANNELS, rate=audio_config.RATE,
						  input=True, frames_per_buffer=audio_config.CHUNK)
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	while signal_queue.empty():
		audio_data_clear = audio_stream.read(audio_config.CHUNK)
		audio_data_encrypted = utils.sxor(audio_data_clear)
		if queue__frames_to_save is not None:
			queue__frames_to_save.put(audio_data_clear)
		udp.sendto(audio_data_encrypted,
				   (server_config.SERVER_AUDIO_RECEIPT__ADDRESS, server_config.SERVER_AUDIO_RECEIPT__PORT))
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	udp.close()


def udp_receive_audio(queue, signal_queue, queue__frames_to_play, queue__frames_to_save=None):
	logging.debug("About to start streaming UDP")
	dict_queue__incoming_frames = {}
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udp.bind((server_config.SERVER_AUDIO_RECEIPT__ADDRESS, server_config.SERVER_AUDIO_RECEIPT__PORT))
	while signal_queue.empty():
		sound_data, address = udp.recvfrom(audio_config.CHUNK * audio_config.CHANNELS * 2)
		if address not in dict_queue__incoming_frames.keys():
			dict_queue__incoming_frames[address] = Queue()

		dict_queue__incoming_frames[address].put(sound_data)

		if queue__frames_to_play is not None:
			queue__frames_to_play.put(sound_data)
		if queue__frames_to_save is not None:
			queue__frames_to_save.put(sound_data)
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	udp.close()


def play_audio(queue, signal_queue, queue__frames_to_play, queue__participant_count):
	# TODO Clean up pyaudio streams. Refer to </unit-test/wav_merge/record.py>
	logging.debug("About to start playing audio")
	p = pyaudio.PyAudio()
	stream = p.open(format=audio_config.FORMAT, channels=audio_config.CHANNELS,
					rate=audio_config.RATE, output=True, frames_per_buffer=audio_config.CHUNK)
	while signal_queue.empty():
		participant_count = queue__participant_count.get(block=True)
		while queue__participant_count.empty() and signal_queue.empty():
			if not queue__frames_to_play.empty():
				alpha = queue__frames_to_play.get(block=True)
				stream.write(utils.sxor(alpha), audio_config.CHUNK)
			else:
				stream.write(chr(128) * audio_config.CHUNK * 4, audio_config.CHUNK)
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	q_utils.clear_queue(queue__frames_to_play)


# def merge_audio_chunks(queue, participant_count):
# 	new_data = 0
# 	for i in range(participant_count):
# 		new_data += numpy.fromstring(queue.get(block=True), numpy.int16) * (1.0/participant_count)
# 	return new_data.tostring()
