'''
namesdict.py names_file output
Builds dictionary linking Wiktionary tags with
language names based on file with correspondence
on each line in format:
	["TAG"] = "NAME"
'''
import pickle
import sys

f = open(sys.argv[1], "r")
d = dict()
for line in f:
	parse = line.split('"')
	if len(parse) == 5:
		d[parse[1]] = parse[3]
	
pickle.dump(d, open(sys.argv[2], "wb"))
