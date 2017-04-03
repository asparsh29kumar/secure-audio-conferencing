import logging
import time
import struct
import socket
import pyaudio
from unittest import signals
from pydub import AudioSegment
from Queue import Queue
from ...config import server as server_config, audio as audio_config
from ...encrypt import utils
from ...queue import signals, utils as q_utils
from ...encrypt import WELL1024, string__expanded_key

def udp_send_audio(queue, signal_queue, queue__frames_to_save=None):
	p = pyaudio.PyAudio()
	audio_stream = p.open(format=audio_config.FORMAT, channels=audio_config.CHANNELS, rate=audio_config.RATE,
						  input=True, frames_per_buffer=audio_config.CHUNK)
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	while signal_queue.empty():
		audio_data_clear = audio_stream.read(audio_config.CHUNK)
		audio_data_encrypted = utils.encrypt(audio_data_clear, string__expanded_key)
		if queue__frames_to_save is not None:
			queue__frames_to_save.put(audio_data_clear)
		udp.sendto(audio_data_encrypted,
				   (server_config.SERVER_AUDIO_RECEIPT__ADDRESS, server_config.SERVER_AUDIO_RECEIPT__PORT))
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	audio_stream.close()
	p.terminate()
	udp.close()


def udp_receive_audio(queue, signal_queue, dict_queue__incoming_frames):
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


# frames_to_multicast replaces frames_to_play
def multicast_send_audio(queue, signal_queue, queue__frames_to_multicast):
	multicast = (server_config.AUDIO_MULTICAST__ADDRESS, server_config.AUDIO_MULTICAST__PORT)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# sock.settimeout(server_config.AUDIO_MULTICAST__SENDER_TIMEOUT)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

	while signal_queue.empty():
		logging.debug("Entered multicast send loop")
		multicast_data = queue__frames_to_multicast.get(block=True)
		logging.debug("About to multicast raw data")
		sock.sendto(multicast_data.raw_data, multicast)
		logging.debug("Multicasted raw data")
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	sock.close()


def multicast_receive_audio(queue, signal_queue, queue__frames_to_play):
	logging.debug("About to start receiving multicast")
	multicast = (server_config.AUDIO_MULTICAST__ADDRESS, server_config.AUDIO_MULTICAST__PORT)
	receiver_address = (server_config.AUDIO_MULTICAST__RECEIVER_ADDRESS, server_config.AUDIO_MULTICAST__RECEIVER_PORT)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(receiver_address)

	group = socket.inet_aton(server_config.AUDIO_MULTICAST__ADDRESS)
	mreq = struct.pack('=4sL', group, socket.INADDR_ANY)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
	p = pyaudio.PyAudio()
	while signal_queue.empty():
		logging.debug("Entered multicast receipt loop")
		sound_data, address = sock.recvfrom(audio_config.CHUNK * audio_config.CHANNELS * 2)
		audio_segment_data = AudioSegment(data=sound_data,
										  sample_width=p.get_sample_size(format=audio_config.FORMAT),
										  frame_rate=audio_config.RATE,
										  channels=audio_config.CHANNELS)
		queue__frames_to_play.put(audio_segment_data)
		logging.debug("Wrote multicasted audio segment to queue")
	p.terminate()
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	sock.close()


def mix_audio(queue, signal_queue, dict_queue__incoming_frames, queue__frames_to_play, queue__frames_to_save):
	logging.debug("About to mix audio streams")
	p = pyaudio.PyAudio()
	while signal_queue.empty():
		if len(dict_queue__incoming_frames) > 0:
			sliced_audio_segments = []
			incoming_stream_count = 0
			for index in range(len(dict_queue__incoming_frames)):
				sliced_audio_segments.append(AudioSegment(
					data=dict_queue__incoming_frames.values()[index].get(block=True),
					sample_width=p.get_sample_size(format=audio_config.FORMAT),
					frame_rate=audio_config.RATE,
					channels=audio_config.CHANNELS))
				incoming_stream_count += 1
			merged = sliced_audio_segments[0]

			for index in range(1, incoming_stream_count):
				merged = merged.overlay(sliced_audio_segments[index])
			queue__frames_to_play.put(merged)
			queue__frames_to_save.put(merged)
	p.terminate()
	signal_data = signal_queue.get(block=True)
	assert signal_data == signals.SIG_FINISH


def play_audio(queue, signal_queue, queue__frames_to_play):
	logging.debug("About to start playing audio")
	p = pyaudio.PyAudio()
	stream = p.open(format=audio_config.FORMAT, channels=audio_config.CHANNELS,
					rate=audio_config.RATE, output=True, frames_per_buffer=audio_config.CHUNK)
	start_time = time.time()
	last_purge_time = 0
	while signal_queue.empty():
		if not queue__frames_to_play.empty():
			alpha = queue__frames_to_play.get(block=True)
			stream.write(utils.decrypt(alpha.raw_data, string__expanded_key), audio_config.CHUNK)
			purge_time = int(time.time() - start_time)
			if purge_time % audio_config.PURGE_INTERVAL == 0 and purge_time != last_purge_time:
				# TODO Don't purge the entire queue. Maybe, about half-way.
				q_utils.clear_queue(queue__frames_to_play)
				last_purge_time = purge_time
			# TODO Figure out when and where to decrypt the audio segments.
		else:
			stream.write(chr(128) * audio_config.CHUNK * 10, audio_config.CHUNK)
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	q_utils.clear_queue(queue__frames_to_play)
	stream.close()
	p.terminate()
