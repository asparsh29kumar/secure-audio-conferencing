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
WAVE_OUTPUT_FILENAME = "serverFile.wav"

p = pyaudio.PyAudio()


def udpStream(CHUNK):
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(("127.0.0.1", 12344))
    while True:
        soundData, addr = udp.recvfrom(CHUNK * CHANNELS * 2)
        frames.append(soundData)
        framesToSave.append(soundData)
        # print soundData
    udp.close()


def play(stream, CHUNK):
    BUFFER = 10
    while True:
        if len(frames) == BUFFER:
            while True:
                alpha = frames.pop(0)
                # stream.write(alpha, CHUNK)
                # stream.write(utils.reversed_string(alpha), CHUNK)
                # stream.write(str(rotate(sxor(alpha, "7"*len(alpha), -200)), CHUNK))
                stream.write(utils.sxor(alpha), CHUNK)
                # stream.write(alpha, CHUNK)


def save():
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(p.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    while True:
        if len(framesToSave) > 0:
            waveFile.writeframes(b''.join(framesToSave.pop(0)))


# if __name__ == "__main__":
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK,
                )

Ts = Thread(target=udpStream, args=(CHUNK,))
Tp = Thread(target=play, args=(stream, CHUNK,))
TSave = Thread(target=save)
Ts.setDaemon(True)
Tp.setDaemon(True)
TSave.setDaemon(True)
Ts.start()
Tp.start()
TSave.start()
Ts.join()
Tp.join()
TSave.join()
