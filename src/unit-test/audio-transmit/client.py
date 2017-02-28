import pyaudio
import socket
from threading import Thread
import utils

frames = []

def udpStream():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
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

# if __name__ == "__main__":

FORMAT = pyaudio.paInt16
CHUNK = 1024
CHANNELS = 2
RATE = 44100

p = pyaudio.PyAudio()

stream = p.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                input = True,
                frames_per_buffer = CHUNK,
                )

Tr = Thread(target = record, args = (stream, CHUNK,))
Ts = Thread(target = udpStream)
Tr.setDaemon(True)
Ts.setDaemon(True)
Tr.start()
Ts.start()
Tr.join()
Ts.join()