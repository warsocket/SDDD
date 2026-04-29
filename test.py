#!/usr/bin/env python3
from sddd import *

sound = Noise()[:10]
for _ in range(10):
	sound = LowpassGenerator(sound, Const(0.5))
sound *= 2

with open("test.wav", "wb") as f:
	f.write(wav_file( sound.emit() ))