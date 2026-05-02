#!/usr/bin/env python3
from sddd import *

# sound = SymmSignal(440,lambda x:x**0.5) - SymmSignal(440,lambda x:x**2) + SymmSignal(440,lambda x:x)  
# sound = sound[:2] *0.9


sound = (Sin(440)**(Sin(44)+1))[:1]

with open("example.wav", "wb") as f:
	f.write(wav_file( sound.emit() ))