#TODO: Deal with parentheses meaning optional - split into two transcripts?

import time
import sys
from collections import Counter

INPUT = "grep.txt"
OUTPUT = sys.argv[1]
DELIMITER = "⦀"

start_time = time.time()

def convert(transcript, language):
	word = []
	word = ["#_"]
	for c in transcript:
		if c == "." or c == "ˈ":
			continue
		word.append(c)# + "_" + language)
	word.append("_#")
	return word

r = open(INPUT, "r")
bad = 0
lang_counts = Counter()
data = []

for line in r:
	print(line)
	lang = ""
	transcripts = []
	string = line.split("{")[2].split("}")[0]
	parse = string.split("|")
	if parse[0] != "IPA":
		bad += 1
		continue
	for element in parse:
		if len(element) < 4:
			continue
		elif element[0:5] == "lang=":
			lang = element.split("=")[1]
#			if len(lang) > 3: # Excludes a few langauges (Scots, etc) w/o 2 letter codes
#				lang = ""
		elif (element[0] == "/" or element[0] == "[") and (element[-1] == "/" or element[-1] == "]"): # Transcript
			if len(element) > 1 and element[1] != "-" and ";" not in element: # ; exlucdes transcripts w/ subscripts - mainly affects ki language
				transcripts.append(element[1:-1])
			
	if lang == "":
		bad += 1
		continue
	elif transcripts == []:
		bad += 1
		continue
	
	for transcript in transcripts:
		lang_counts[lang] += 1
		data.append((transcript, lang))
						
w = open(OUTPUT, "w")
for (transcript, lang) in data:
	w.write(lang + DELIMITER + transcript + "\n")
