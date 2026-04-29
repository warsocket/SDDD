#!/usr/bin/env python3
from sddd import *


# use polyphone -1 -i export.sfz -o instrument  to convert

def sample(f): 
	return Sin(f)[:1/f]

emit_sfz(sample)