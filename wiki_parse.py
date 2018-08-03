# encoding: utf-8

# grep -o "{{IPA|.*}}" enwiktionary-20180420-pages-articles.xml > grep.txt

import time
import sys
from collections import Counter
import pickle
import io

INPUT = sys.argv[1]
OUTPUT = sys.argv[2]
DELIMITER = "⦀"
NAMES = pickle.load(open("langs.pydict", "rb"))

start_time = time.time()

r = io.open(INPUT, "r", encoding="utf-8")
bad = 0
lang_counts = Counter()
data = []

for line in r:
	print(line.encode('utf-8'))
	lang = ""
	transcripts = []
	
	string = line.split("{{")[1].split("}}")[0]
	for string in line.split("{{"):
		if "}}" not in string:
			continue
		parse = string.split("}}")[0].split("|")
		if parse[0] != "IPA":
			bad += 1
			continue
		for element in parse:
			if len(element) < 4:
				continue
			elif element[0:5] == "lang=":
				lang = element.split("=")[1]
#				if len(lang) > 3: # Excludes a few langauges (Scots, etc) w/o 2 letter codes
#					lang = ""
			elif (element[0] == "/" or element[0] == "[") and (element[-1] == "/" or element[-1] == "]"): # Transcript
				if len(element) > 1 and element[1] == "-" or ";" in element: # ; exlucdes transcripts w/ subscripts - mainly affects ki language
					pass
				elif "(" in element and ")" in element and len(element.split("(")[1].split(")")[0]) == 1: # Optional phones
					transcripts.append(element[1:-1])
					transcripts.append(element[1:-1].replace("(", "").replace(")", ""))
				else:
					transcripts.append(element[1:-1])
			
	if lang == "":
		bad += 1
		continue
	elif transcripts == []:
		bad += 1
		continue
	
	for transcript in transcripts:
		lang_counts[lang] += 1
		lang_name = NAMES.get(lang, lang) # Full language name
		data.append((transcript, NAMES.get(lang, lang)))
						
w = io.open(OUTPUT, "w", encoding="utf-8")
for (transcript, lang) in data:
	w.write(lang + DELIMITER + transcript + "\n")
