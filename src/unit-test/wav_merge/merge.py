from pydub import AudioSegment
from pydub.playback import play

sound1 = AudioSegment.from_file("./file1.wav")
sound2 = AudioSegment.from_file("./file2.wav")

combined = sound1.overlay(sound2)

play(combined)
# combined.export("./combined.wav", format='wav')
