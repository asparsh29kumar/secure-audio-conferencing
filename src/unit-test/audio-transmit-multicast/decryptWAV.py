import utils
import wave
import pyaudio
CHANNELS = 2
RATE = 44100
FORMAT = pyaudio.paInt16
WAVE_INPUT_FILENAME = "serverFile.wav"
WAVE_OUTPUT_FILENAME = "serverCrunchedFile.wav"
frames = []
waveInputFile = wave.open(WAVE_INPUT_FILENAME, 'rb')
waveOutputFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveOutputFile.setnchannels(CHANNELS)
waveOutputFile.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
waveOutputFile.setframerate(RATE)
for i in range(waveInputFile.getnframes()):
	frames.append(utils.sxor(waveInputFile.readframes(1)))
	waveOutputFile.writeframes(b''.join(frames.pop(0)))
waveInputFile.close()
waveOutputFile.close()