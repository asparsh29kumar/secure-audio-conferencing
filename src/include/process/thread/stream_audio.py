import logging
import socket
import pyaudio
from unittest import signals
from pydub import AudioSegment
from Queue import Queue
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
		audio_data_encrypted = utils.encrypt(audio_data_clear)
		if queue__frames_to_save is not None:
			queue__frames_to_save.put(audio_data_clear)
		udp.sendto(audio_data_encrypted,
				   (server_config.SERVER_AUDIO_RECEIPT__ADDRESS, server_config.SERVER_AUDIO_RECEIPT__PORT))
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	udp.close()


def udp_receive_audio(queue, signal_queue, dict_queue__incoming_frames):
	logging.debug("Type of signal_queue: %s", type(signal_queue))
	logging.debug("About to start streaming UDP")
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udp.bind((server_config.SERVER_AUDIO_RECEIPT__ADDRESS, server_config.SERVER_AUDIO_RECEIPT__PORT))
	while signal_queue.empty():
		sound_data, address = udp.recvfrom(audio_config.CHUNK * audio_config.CHANNELS * 2)
		if address not in dict_queue__incoming_frames.keys():
			dict_queue__incoming_frames[address] = Queue()
		dict_queue__incoming_frames[address].put(sound_data)

	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	udp.close()


def mix_audio(queue, signal_queue, dict_queue__incoming_frames, queue__frames_to_play, queue__frames_to_save):
	logging.debug("About to mix audio streams")
	while signal_queue.empty():
		if len(dict_queue__incoming_frames) > 0:
			sliced_audio_segments = []
			incoming_stream_count = 0
			for index in range(len(dict_queue__incoming_frames)):
				sliced_audio_segments.append(AudioSegment(
					data=dict_queue__incoming_frames.values()[index].get(block=True),
					sample_width=pyaudio.PyAudio().get_sample_size(format=audio_config.FORMAT),
					frame_rate=audio_config.RATE,
					channels=audio_config.CHANNELS))
				incoming_stream_count += 1
			merged = sliced_audio_segments[0]

			for index in range(1, incoming_stream_count):
				merged = merged.overlay(sliced_audio_segments[index])
			queue__frames_to_play.put(merged)
			queue__frames_to_save.put(merged)
	signal_data = signal_queue.get(block=True)
	assert signal_data == signals.SIG_FINISH


def play_audio(queue, signal_queue, queue__frames_to_play, queue__participant_count):
	# TODO Clean up pyaudio streams. Refer to </unit-test/wav_merge/record.py>
	logging.debug("About to start playing audio")
	p = pyaudio.PyAudio()
	stream = p.open(format=audio_config.FORMAT, channels=audio_config.CHANNELS,
					rate=audio_config.RATE, output=True, frames_per_buffer=audio_config.CHUNK)
	while signal_queue.empty():
		# TODO Use participant_count for UI.
		participant_count = queue__participant_count.get(block=True)
		while queue__participant_count.empty() and signal_queue.empty():
			if not queue__frames_to_play.empty():
				alpha = queue__frames_to_play.get(block=True)
				# TODO Figure out when and where to decrypt the audio segments.
				stream.write(utils.decrypt(alpha.raw_data), audio_config.CHUNK)
			else:
				stream.write(chr(128) * audio_config.CHUNK * 4, audio_config.CHUNK)
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	q_utils.clear_queue(queue__frames_to_play)
