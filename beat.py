#!/usr/bin/env python3
from sddd import *


freq = Notes[0]
octaves = 3
df = 1

fm = RampGenerator(lambda x: 1-x**0.5, 0.25)*octaves
sound = ((Sin(freq)*0.5+Square(freq)*0.25) % fm)

sound *= RampGenerator(lambda x: 1-x**df, 0.25)

with open("beat.wav", "wb") as f:
	f.write(wav_file( sound.emit() ))