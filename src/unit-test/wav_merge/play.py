from pydub import AudioSegment, playback

sound = AudioSegment.from_file("./sample.wav")
playback.play(sound)
