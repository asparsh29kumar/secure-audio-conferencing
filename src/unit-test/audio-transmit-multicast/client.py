import pyaudio
import socket
from threading import Thread
import utils
import wave
import struct

multicast_group = '224.3.29.71'

frames = []
framesToSave = []

FORMAT = pyaudio.paInt16
CHUNK = 1024
CHANNELS = 2
RATE = 44100
WAVE_OUTPUT_FILENAME = "clientFile.wav"

p = pyaudio.PyAudio()

group = socket.inet_aton(multicast_group)
mreq = struct.pack('=4sL', group, socket.INADDR_ANY)

def udpStream():
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udp.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
	while True:
		if len(frames) > 0:
			udp.sendto(frames.pop(0), ("127.0.0.1", 12344))
	udp.close()


def record(stream, CHUNK):
	while True:
		alpha = stream.read(CHUNK)
		# frames.append(alpha)
		# frames.append(utils.reversed_string(alpha))
		# frames.append(rotate(sxor(alpha), 200))
		frames.append(utils.sxor(alpha))
		framesToSave.append(alpha)


def save():
	waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	waveFile.setnchannels(CHANNELS)
	waveFile.setsampwidth(p.get_sample_size(FORMAT))
	waveFile.setframerate(RATE)
	while True:
		if len(framesToSave) > 0:
			waveFile.writeframes(b''.join(framesToSave.pop(0)))


# if __name__ == "__main__":
stream = p.open(format = FORMAT,
				channels = CHANNELS,
				rate = RATE,
				input = True,
				frames_per_buffer = CHUNK,
				)

Tr = Thread(target = record, args = (stream, CHUNK,))
Ts = Thread(target = udpStream)
TSave = Thread(target = save)
Tr.setDaemon(True)
Ts.setDaemon(True)
TSave.setDaemon(True)
Tr.start()
Ts.start()
TSave.start()
Tr.join()
Ts.join()
TSave.join()
