#!/usr/bin/env python3
from sddd import *

sound = (Sin(500) % 1.0)[:5.0] << Square(500)[:2]

with open("out.wav", "wb") as f:
	f.write(wav_file( sound.emit() ))