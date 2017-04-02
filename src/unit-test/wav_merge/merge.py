from pydub import AudioSegment

sound1 = AudioSegment.from_file("./file1.wav")
sound2 = AudioSegment.from_file("./file2.wav")

combined = sound1.overlay(sound2)

# combined.export("./combined.wav", format='wav')
