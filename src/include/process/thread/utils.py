import logging
import wave
from ...queue import signals, utils as q_utils


def save_audio(queue, signal_queue, file_name, channels, channel_format, channel_rate, p, queue__frames_to_save):
	logging.debug("About to start saving audio")
	wave_file = wave.open(file_name, 'wb')
	wave_file.setnchannels(channels)
	wave_file.setsampwidth(p.get_sample_size(channel_format))
	wave_file.setframerate(channel_rate)
	while signal_queue.empty():
		if not queue__frames_to_save.empty():
			wave_file.writeframes(b''.join(queue__frames_to_save.get(block=True)))
	signal_queue_data = signal_queue.get(block=True)
	assert signal_queue_data == signals.SIG_FINISH
	q_utils.clear_queue(queue__frames_to_save)
