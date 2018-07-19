'''
Splits newline-separated data into training, validation, optional test
sets (80-10-10 or 90-10).
split.py data_path training_path val_path (test_path)
'''
import random
import sys

f = open(sys.argv[1])
r = open(sys.argv[2], "w")
v = open(sys.argv[3], "w")
s = None
if len(sys.argv) >= 5:
	open(sys.argv[4], "w")

for line in f:
	n = random.randint(0, 9)
	if n == 0:
		v.write(line)
	elif n == 1 and s is not None:
		s.write(line)
	else:
		r.write(line)
	
