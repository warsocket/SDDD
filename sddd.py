#!/usr/bin/env python3

# SDDD:
# SFX
# DSL
# DAG
# DAW

import copy
import math
import random
import struct

# d = struct.pack("H",1)
# print(d)


#12 / oct chromatic
Notes = [440 * (2**(1/12))**i for i in range(-12*3,12*3+1)]
Notes_names = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]


def wav_file(data,freq=44100):	
	"""
	#MAIN HEADER
	#signature
	signature = b"RIFF"
	#filesize from after this field
	size = b"\x00\x00\x00\x00"
	#subtype of RIFF
	subtype = b"WAVE"

	#FMT CHUNK
	#chunk id
	fmt_signature = b"fmt "
	#chunk size after this field
	fmt_size = b"\x00\x00\x00\x00"
	#audio format
	audio_format = b"\x00\x00"
	#num Chnnels
	num_channels b"\x00\x00"
	#sampleRate
	sample_rate = b"\x00\x00\x00\x00"
	#byterate [SampleRate * NumChannels * (BitsPerSample / 8)]
	byte_rate = b"\x00\x00\x00\x00"
	#BlockAlign [NumChannels * (BitsPerSample / 8)]
	block_align = b"\x00\x00"
	#BitsPerSample [(BitsPerSample / 8)]
	bits_per_sample = b"\x00\x00"

	#FACT CHUNK
	fact_signature = b"fact"
	fact_size = b"\x00\x00\x00\x00"
	fact_num_samples = b"\x00\x00\x00\x00"

	#DATA CHUNK
	data_signature = b"data"
	data_size = b"\x00\x00\x00\x00"
	#data = []
	"""

	# now we do real filling for float wav

	# data is a list of floats, freq is sample rate
	num_samples = len(data)
	
	# MAIN HEADER
	# signature
	signature = b"RIFF"
	# filesize from after this field: 4 (WAVE) + 24 (fmt) + 12 (fact) + 8 (data header) + actual data
	# size = struct.pack('<I', 50-2?? + (num_samples * 4))
	# size = struct.pack('<I', 36 + 12*1 + (num_samples * 2))
	size = struct.pack('<I', 36 + 12*1 + (num_samples * 2))


	# subtype of RIFF
	subtype = b"WAVE"

	# FMT CHUNK
	# chunk id
	fmt_signature = b"fmt "
	# chunk size after this field
	fmt_size = struct.pack('<I', 16)
	# audio format (1 = PCM,3 = IEEE float)
	# audio_format = struct.pack('<H', 3)
	audio_format = struct.pack('<H', 1)

	# num Channels (1 = mono)
	num_channels = struct.pack('<H', 1)
	# sampleRate
	sample_rate = struct.pack('<I', freq)
	# byterate [SampleRate * NumChannels * (BitsPerSample / 8)]
	# byte_rate = struct.pack('<I', freq * 1 * 4)
	byte_rate = struct.pack('<I', freq * 1 * 2)

	# BlockAlign [NumChannels * (BitsPerSample / 8)]
	# block_align = struct.pack('<H', 1 * 4)
	block_align = struct.pack('<H', 1 * 2)

	# BitsPerSample [BitsPerSample]
	# bits_per_sample = struct.pack('<H', 32)
	bits_per_sample = struct.pack('<H', 16)


	# FACT CHUNK
	# signature
	fact_signature = b"fact"
	# chunk size after this field
	fact_size = struct.pack('<I', 4)
	# number of samples
	fact_num_samples = struct.pack('<I', num_samples)

	# DATA CHUNK
	# signature
	data_signature = b"data"
	# size of audio data in bytes
	# data_size = struct.pack('<I', num_samples * 4)
	data_size = struct.pack('<I', num_samples * 2)

	# actual audio payload
	# audio_data = b"".join(struct.pack('<f', s) for s in data)
	audio_data = b"".join(struct.pack('<h', int(min(max(s,-1.0),1.0)*0x7FFF) ) for s in data)


	# assemble all pieces
	return (signature + size + subtype + 
			fmt_signature + fmt_size + audio_format + num_channels + 
			sample_rate + byte_rate + block_align + bits_per_sample + 
			fact_signature + fact_size + fact_num_samples + 
			data_signature + data_size + audio_data)
	# return (signature + size + subtype + 
	# 		fmt_signature + fmt_size + audio_format + num_channels + 
	# 		sample_rate + byte_rate + block_align + bits_per_sample + 
	# 		data_signature + data_size + audio_data)

def emit_sfz_oneshot(generator_factory):

	sfz_f = open("./sfz/export.sfz", "w")
	# Start the SFZ file with a group definition
	sfz_f.write("<group>\n")

	for index,note in enumerate(Notes):
		print(f"{index+1}/{len(Notes)}")
		gen = generator_factory(note)

		audio_data = gen.emit()
		with open(f"./sfz/{index}.wav", "wb") as f:
			f.write(wav_file( audio_data ))

		# Map the frequency index to the actual MIDI note (i=0 is MIDI 33)
		midi_note = 69 + (index - 36)
		
		# Write the region mapping for this specific sample
		sfz_f.write(f"<region> sample={index}.wav lokey={midi_note} hikey={midi_note} pitch_keycenter={midi_note} loop_mode=one_shot\n")

	sfz_f.close()




def emit_sfz(generator_factory, loop_start=0):

	sfz_f = open("./sfz/export.sfz", "w")
	# Start the SFZ file with a group definition
	sfz_f.write("<group>\n")

	for index,note in enumerate(Notes):
		print(f"{index+1}/{len(Notes)}")
		gen = generator_factory(note)

		audio_data = gen.emit()
		with open(f"./sfz/{index}.wav", "wb") as f:
			f.write(wav_file( audio_data ))

		# Map the frequency index to the actual MIDI note (i=0 is MIDI 33)
		midi_note = 69 + (index - 36)
		
		# Write the region mapping for this specific sample
		sfz_f.write(f"<region> sample={index}.wav lokey={midi_note} hikey={midi_note} pitch_keycenter={midi_note} loop_mode=loop_continuous loop_start={loop_start} loop_end={len(audio_data)}\n")
	sfz_f.close()



class Generator():
	def __init__(self):
		self.t = 0 # Initialize time at zero

	def seek(self,tx):
		self.t += tx
		return self

	def reset(self):
		self.t = 0

	def emit(self, freq=44100):

		data = []
		divisor = freq/math.tau
		val = self.get()
		while val != None:
			data.append( val )
			self.seek(1.0/freq)
			val = self.get()

		return data

	def clone(self):
		return copy.deepcopy(self)


	#Ergonomic functions

	def _wrap(self, other):
		return other if isinstance(other, Generator) else Const(other)

	def __add__(self, other):
		return MixGenerator(lambda a, b: a + b, self, self._wrap(other))

	def __sub__(self, other):
		return MixGenerator(lambda a, b: a - b, self, self._wrap(other))

	def __mul__(self, other):
		return MixGenerator(lambda a, b: a * b, self, self._wrap(other))

	def __truediv__(self, other):
		return MixGenerator(lambda a, b: a / b if b != 0 else 0, self, self._wrap(other))

	def __mod__(self, other):
		return FMGenerator(self._wrap(other), self)

	def __rmod__(self, other):
		return FMGenerator(self, self._wrap(other))

	def __invert__(self):
		return self*-1.0

	# todo specific  more better implementation for seqiuence generator
	def __lshift__(self, other):
		return SequenceGenerator(self, other)

	def __rshift__(self, other):
		return SequenceGenerator(self, other)

	def __getitem__(self, s):
		if isinstance(s, slice):
			res = self.clone()
			
			# 1. Begrens de eindtijd (y)
			if s.stop is not None:
				res = FiniteGenerator(res, s.stop)
				
			# 2. Verschuif naar de starttijd (x)
			if s.start is not None and s.start > 0:
				res.seek(s.start)
				
			return res
		else:
			return self



	# So you can prefix your Bare Const ie: 0.5*Sin(3000) 
	def __radd__(self, other): return self.__add__(other)
	def __rmul__(self, other): return self.__mul__(other)
	def __rsub__(self, other): return self._wrap(other).__sub__(self)



#UNNARY GENARATOR
class PeriodicGenerator(Generator):
	def __init__(self, op, freq, offset=0.0):
		super().__init__()
		self.op = op     # The periodic function, e.g., math.sin
		self.freq = freq # Frequency in Hz
		self.offset = offset

	def get(self):
		# We pass the phase (t * tau) to the operator
		# t is seconds, freq is Hz -> t * freq = cycles
		return self.op( (self.t * math.tau + self.offset)   * self.freq )



class FMGenerator(Generator):
	def __init__(self, fm, g):
		super().__init__()
		self.g = g 
		self.fm = fm

	def get(self):
		# We pakken simpelweg de huidige sample van g
		if self.fm.get() == None: return None
		return self.g.get()

	def seek(self, tx):
		speed = self.fm.get()
		if speed is None:
			return
		
		speed = 2**speed

		self.g.seek(speed*tx)
		self.fm.seek(tx)
		# super().seek(tx)

		return self

	def reset(self):
		self.g.reset()
		self.fm.reset()


class RampGenerator(Generator):
	def __init__(self, f, duration):
		super().__init__()
		self.f = f 
		self.duration = duration

	def get(self):
		if self.t > self.duration:
			return None
		else:
			return self.f(self.t / self.duration)


class FiniteGenerator(Generator):
	def __init__(self, gen, duration):
		super().__init__()
		self.gen = gen
		self.duration = duration

	def get(self):
		if self.t > self.duration:
			return None
		else:
			return self.gen.get()

	def seek(self, tx):
		super().seek(tx)
		self.gen.seek(tx)
		return self

	def reset(self):
		self.gen.reset()



class SequenceGenerator(Generator):
	def __init__(self, *generators):
		super().__init__()
		self.generators = list(generators)
		self.generators.reverse()
		self.backup_gens = list(map(lambda x: x.clone(), self.generators))

	def seek(self, tx):
		if self.generators:
			self.generators[-1].seek(tx)
			if self.generators[-1].get() == None:
				self.generators.pop()

		return self

	def get(self):
		if not self.generators: return None
		return self.generators[-1].get()

	def reset(self):
		self.generators = list(map(lambda x: x.clone(), self.backup_gens))
		


class LoopGenerator(Generator):
	def __init__(self, gen):
		super().__init__()
		self.gen = gen()

	def seek(self, tx):
		super().seek(tx)
		if self.get() == None: self.reset()
		return self

	def reset(self):
		self.gen.reset()



class MixGenerator(Generator):
	def __init__(self, op, *generators):
		super().__init__()
		self.op = op
		self.generators = generators

	def get(self):
		# Haal van alle generators de sample op
		samples = [gen.get() for gen in self.generators]

		if any(s is None for s in samples):
			return None

		return self.op(*samples)

	def seek(self, tx):
		for gen in self.generators:
			gen.seek(tx)

		return self


	def reset(self):
		for g in self.generators:
			g.reset()


class LowpassGenerator(Generator):
	def __init__(self, gen, alpha_gen):
		super().__init__()
		self.gen = gen
		self.alpha_gen = alpha_gen
		
		# Initialisatie van de eerste waarde
		self.current_val = gen.get()

	def seek(self, tx):
		# Update eerst de bron en de alpha-parameter
		self.gen.seek(tx)
		self.alpha_gen.seek(tx)
		
		fresh = self.gen.get()
		alpha = self.alpha_gen.get()
		
		# Stop als een van de generators None geeft
		if fresh is None or alpha is None:
			self.current_val = None
			return self

		# De filter berekening met de dynamische alpha
		self.current_val = (self.current_val * alpha) + (fresh * (1.0 - alpha))
		return self

	def get(self):
		return self.current_val

	def reset(self):
		self.gen.reset()
		self.alpha_gen.reset()



# From here on only Fluff (ergonomic notation but no new functionality)


def Sin(freq, offset=0.0):
	return PeriodicGenerator(math.sin, freq, offset)

def Cos(freq, offset=0.0):
	return PeriodicGenerator(math.cos, freq, offset)

def Const(value):
	return PeriodicGenerator(lambda _: value, 0.0)

def Zero():
	return Const(0.0)

def One():
	return Const(1.0)



def square(t):
	t %= math.tau
	return [-1,1][t< math.pi] 

def Square(freq, offset=0.0):
	return PeriodicGenerator(square, freq, offset)


def triangle(t):
    return 2 / math.pi * math.asin(math.sin(t))

def Triangle(freq, offset=0.0):
    return PeriodicGenerator(triangle, freq, offset)



def saw(t):
	phase = (t % math.tau) / math.tau
	return phase*2-1

def Saw(freq, offset=0.0):
	return PeriodicGenerator(saw, freq, offset)


def white_noise(t):
    return random.uniform(-1.0, 1.0)

def Noise():
    return PeriodicGenerator(white_noise, 0.0)


def dsaw(t):
	phase = (t % math.tau) / math.tau
	
	if phase < 0.5:
		return phase * 2
	return (phase - 0.5) * -2


def DSaw(freq, offset=0.0):
	return PeriodicGenerator(dsaw, freq, offset)



def mk_signal_generator(f, width=0.5):

	def sig_gen(t):
		phase = (t % math.tau) / math.tau
		
		if phase < width:
			x = phase / width
			return f(x)
		else:
			x = (phase - width) / (1 - width)
			return -f(x)

	return sig_gen


def Signal(freq, f, width=0.5, offset=0.0):
	return PeriodicGenerator(mk_signal_generator(f,width), freq, offset)



def mk_symm_generator(f):
	def sig_gen(t):
		phase = (t % math.tau) / math.tau
		
		# We verdelen de fase in 4 gelijke stukken
		if phase < 0.25:
			# 1. Omhoog: 0 -> 1
			return f(phase * 4)
		elif phase < 0.50:
			# 2. Terug: 1 -> 0
			return f(1 - (phase - 0.25) * 4)
		elif phase < 0.75:
			# 3. Omlaag: 0 -> -1
			return -f((phase - 0.50) * 4)
		else:
			# 4. Terug: -1 -> 0
			return -f(1 - (phase - 0.75) * 4)
			
	return sig_gen

def SymmSignal(freq, f, offset=0.0):
	return PeriodicGenerator(mk_symm_generator(f), freq, offset)
