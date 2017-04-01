import pyaudio
import socket
from threading import Thread
import utils
import wave

frames = []
framesToSave = []

FORMAT = pyaudio.paInt16
CHUNK = 1024
CHANNELS = 2
RATE = 44100
WAVE_OUTPUT_FILENAME = "clientFile.wav"

p = pyaudio.PyAudio()


def udp_send_audio(stream, chunk_size):
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	while True:
		alpha = stream.read(chunk_size)
		frames.append(utils.sxor(alpha))
		framesToSave.append(alpha)
		udp.sendto(frames.pop(0), ("127.0.0.1", 12344))
	udp.close()


def save(file_name, channels, channel_format, channel_rate):
	wave_file = wave.open(file_name, 'wb')
	wave_file.setnchannels(channels)
	wave_file.setsampwidth(p.get_sample_size(channel_format))
	wave_file.setframerate(channel_rate)
	while True:
		if len(framesToSave) > 0:
			wave_file.writeframes(b''.join(framesToSave.pop(0)))


audio_stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

Tr = Thread(target=udp_send_audio, args=(audio_stream, CHUNK,))
TSave = Thread(target=save, args=(WAVE_OUTPUT_FILENAME, CHANNELS, FORMAT, RATE))
Tr.setDaemon(True)
TSave.setDaemon(True)
Tr.start()
TSave.start()
Tr.join()
TSave.join()
