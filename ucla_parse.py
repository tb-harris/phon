# TODO:
# Broad vs narrow, phonetic vs phonemic
# numbers? (stress)
# Replace # with #_ and _# ?
# Remove entires w/o numbers?
#
# Manually corrected
# Header tags: kor_word-list_1982_01.html, kor_word-list_1986_01.html
# Cell tags: hye_word-list_1983_01.html, other hye
# Title: guj_word-list_1981_01.html
# Deleted: English (no data)

from html.parser import HTMLParser
from collections import OrderedDict
import sys
import os
import unicodedata
import pickle

DIR = "Language"
SAVE = None # Name of file to save language/transcript pairs
DELIMITER = "⦀" # Separates language name from transcript


if len(sys.argv) != 3 or sys.argv[1].lower() != "-save":
	print("ucla_parse.py -save [file]")
	sys.exit()
else:
	SAVE = sys.argv[2]

class UCLADataParser(HTMLParser):
	'''
	Facilitates the extraction of data table from
	UCLA Phonetics Lab Archive HTML file
	
	Methods:
	* feed(string) - Feeds HTML string for parsing
	
	Attributes:
	* table - 2D list representing extracted table from fed HTML
	* language - Name of language as represented in fed HTML
	'''

	def __init__(self):
		self.table = []
		self.language = ""
		
		# Internal attributes
		self.in_cell = False # True if currently parsing inside cell
		self.in_title = False # True if currently parsing in page title
		self.col = 0 # Column iterator
		self.row = 0 # Row iterator
		self.header_cols = 0 # Number of columns in header
		
		HTMLParser.__init__(self)
		
	def handle_starttag(self, tag, atr):
		''' Called when parser reaches <X>
		'''
		if tag == "th" or tag == "td":
			# Beginning of header or data cell
			self.in_cell = True
		elif tag == "tr":
			# Beginning of row
			self.col = 0 # Resets column iterator
		elif tag == "title":
			# Beginning of page title
			self.in_title = True
			
	def handle_endtag(self, tag):
		''' Called when parser reaches </X>
		'''
		if tag == "th" or tag == "td":
			# End of cell
			self.col += 1 # Increments column iterator
			self.in_cell = False
		elif tag == "tr":
			# End of row
			if self.header_cols == 0:
				# Number of header columns not yet calculated
				self.header_cols = self.col
			if self.col != self.header_cols:
				# Mismatch between number of cells in row and in header
				#print("Incorrect number of cells in row")
				#print(self.language, self.header_cols, self.col)
				del self.table[-1] # Deletes row from parsed table
			else:
				self.row += 1 # Increments row iterator
		elif tag == "title":
			# End of page title
			self.in_title = False
			
	def handle_data(self, data):
		''' Called when parser encounters data (as opposed to tag)
		'''
		
		# Normalization
		# NKCC - Normalizes, decomposes, recomposes
		# NFD - Normalizes, decomposes
		# text = unicodedata.normalize("NFC", data) # normalizes variants of same symbols, fixes xa0 spaces
		text = data
		
		if self.in_cell:
			# Parsing data inside cell
			if self.row >= len(self.table):
				# New row
				self.table.append([])
				
			if len(self.table[-1]) <= self.col:
				# More than one element in cell
				self.table[-1].append(text)

		elif self.in_title:
			# Parsing data inside cell
			
			# Attempt to retrieve name of language
			try:
				self.language = text.split(" ", 3)[3].lower()
			except:
				self.language = "null"	
			if self.language.isspace():
				self.language = "null"

def get_transcript_index(parse):
	'''
	Guesses index of column of parsed UCLA table that
	has transcripts of words in target language based
	on header content and column positions
	
	Arguments:
	* parse - Instance of UCLADataParser() that has been fed HTML data
	
	Return:
	* Integer value of target column's index
	'''

	cols = [] # Stores indices of columns that have neither favorable nor disfavorable indicators
	
	# Set of header substrings that suggest column contains transcripts
	FAVORABLE = {"ipa", "transcription", "transcript", "phonetic", parse.language}
	
	# Set of header substrings that suggest column does not contain transcripts
	DISFAVORABLE = {"entry", "sound", "orthography", "gloss", "illustrated", "note", "english", "semantic", "romanization", "phonem", "transliteration", "sound", "click", "potential", "recording", "root", "ending", "section", "manner", "orthographic", " script", "contrast", "board"}
	
	for i, header in enumerate(parse.table[0]): # Enumerate through headers
		if any(substring.lower() in header.lower() for substring in DISFAVORABLE):# or parse.table[i][1].isdigit(): # or (len(table[0]) > 2 and row == len(table[0]) - 1):
			# Header contains disfavorable string or col's first non-header row contains number or is last col of >2 col table
			continue
		elif any(substring.lower() in header.lower() for substring in FAVORABLE):
			# Header contains favorable string - returned immediately
			return i
		else:
			# Neutral classification (no favorable or disfavorable indicators)
			cols.append(i)
	
	# No columns with favorable indicators found - first neutral column (if any) returned		
	if len(cols) > 0:
		return cols[0]
	else:
		return None

def get_transcripts(f):
	'''
	Returns list of transcripts from UCLA Phon Lab
	HTML file
	
	Arguments:
	* f - DirEntry object (ie returned from os.scandir())
	
	Return:
	* List of untokenized transcript strings, or empty list
	'''
	
	# Set of substrings that suggest transcript is actually English text
	BAD_TRANSCRIPT = {"transcript", "available"}
	
	string = open(file.path, "r").read() # Gets file contents in string
	parser = UCLADataParser()
	parser.feed(string) # Feeds string to parser
	index = get_transcript_index(parser) # Gets index of transcript col
	parser.close()
	
	if index == None: # No transcript col index
		return []
	else:
		# Returns list of valid transcripts in indicated column 
		return [row[index] for row in parser.table[1:] if not (row[index].isspace() or any(substring.lower() in row[index].lower() for substring in BAD_TRANSCRIPT))]

data = []	

for folder in os.scandir(DIR):
	# Iterates over folders, which correspond to languages, in HTML directory
	if os.path.basename(folder.name) in ["HGM"]: # langs w/o transcriptions
		continue
	for file in os.scandir(folder.path):
		#print(file.path)
		transcripts = get_transcripts(file)
		if transcripts != None:
			data.extend([(transcript, os.path.basename(file.name).split("_")[0].upper()) for transcript in transcripts])
	
f = open(SAVE, "w")
for (transcript, tag) in data:
	f.write(tag + DELIMITER + transcript.replace("\n", " ") + "\n")
