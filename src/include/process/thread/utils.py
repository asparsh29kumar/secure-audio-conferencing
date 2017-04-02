import logging
import wave
import pyaudio
from ...queue import signals, utils as q_utils
from ...config import audio as audio_config


def save_audio(queue, signal_queue, file_name, queue__frames_to_save):
	logging.debug("About to start saving audio")
	wave_file = wave.open(file_name, 'wb')
	wave_file.setnchannels(audio_config.CHANNELS)
	wave_file.setsampwidth(pyaudio.PyAudio().get_sample_size(audio_config.FORMAT))
	wave_file.setframerate(audio_config.RATE)
	while signal_queue.empty():
		if not queue__frames_to_save.empty():
			# wave_file.writeframes(b''.join(queue__frames_to_save.get(block=True)))
			frame_data = queue__frames_to_save.get(block=True)
			# logging.debug("Type of frame_data: %s", type(frame_data))
			audio_segment_raw_data = frame_data.raw_data
			wave_file.writeframes(b''.join(audio_segment_raw_data))
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	q_utils.clear_queue(queue__frames_to_save)


# TODO Remove me. I'm used in the client.
def save_audio__old(queue, signal_queue, file_name, queue__frames_to_save):
	logging.debug("About to start saving audio")
	wave_file = wave.open(file_name, 'wb')
	wave_file.setnchannels(audio_config.CHANNELS)
	wave_file.setsampwidth(pyaudio.PyAudio().get_sample_size(audio_config.FORMAT))
	wave_file.setframerate(audio_config.RATE)
	while signal_queue.empty():
		if not queue__frames_to_save.empty():
			wave_file.writeframes(b''.join(queue__frames_to_save.get(block=True)))
			# frame_data = queue__frames_to_save.get(block=True)
			# logging.debug("Type of frame_data: %s", type(frame_data))
			# audio_segment_raw_data = frame_data.raw_data
			# wave_file.writeframes(b''.join(audio_segment_raw_data))
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	q_utils.clear_queue(queue__frames_to_save)
