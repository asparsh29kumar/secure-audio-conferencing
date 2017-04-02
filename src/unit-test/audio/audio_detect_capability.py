#!/usr/bin/env python
import pyaudio
from pprint import pprint

p = pyaudio.PyAudio()

pprint(p.is_format_supported(input_format=pyaudio.paInt8,
                             input_channels=2,
                             rate=193939,
                             input_device=5))
# try:
#     # stream = p.open(format=pyaudio.paInt8,
#     #                 channels=1,
#     #                 rate=44100,
#     #                 input=True,
#     #                 input_device_index=5,
#     #                 frames_per_buffer=1024)
#     # data = stream.read(1024)
#
# except IOError as e:
#     print e
#
# stream.stop_stream()
# stream.close()

p.terminate()