# TODO:
# Broad vs narrow, phonetic vs phonemic
# numbers? (stress)
# Replace # with #_ and _# ?
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
LOAD = None # Name of file containing language/transcript pairs


if len(sys.argv) > 1:
	if sys.argv != 3:
		print("Improper number of arguments... terminating.")
		sys.exit()
	if sys.argv[1].lower() == "-save":
		SAVE = sys.argv[2]
	elif sys.argv[1].lower() == "-load":
		LOAD = sys.argv[2]
	else:
		print("Unknown argument; valid arguments: -save [file] OR -load [file]")

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
		# NFKC - Normalizes, decomposes, recomposes
		# NFKD - Normalizes, decomposes
		text = unicodedata.normalize("NFKC", data) # normalizes variants of same symbols, fixes xa0 spaces
		
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
		
def tokenize(transcript, tag):
	'''
	Split transcript into symbols, adds
	start/end symbols.
	
	Arguments:
	* transcript - String to tokenize
	* tag - 3-letter language tag
	
	Return:
	* list of tokens
	'''
	
	in_paren = False
	
	tokens = []
	tokens.append("#")
	for c in transcript:
		if c == "(":
			in_paren = True
		elif c == ")":
			in_paren = False
		elif in_paren:
			continue
		elif c.isspace():
			if tokens[-1] != "#":
				tokens.append("#")
		elif c == "/":
			break
		elif c == "|" and tag == "YEY": # YEY: | used like /
			break
		elif c in ["|", "[", "]"]: 
			continue
		else:
			tokens.append(c)
	if tokens[-1] != "#":
		tokens.append("#")
		
	return tokens
	
def add_tags(tokens, tag):
	'''
	Appends "￨" (OpenNMT feature delimiter)
	followed by tag to each element in list
	
	Arguments:
	* tokens - List of elements to be tagged
	* tag - Tag to append to elements
	
	Return:
	* Tagged list
	'''
	return [token + "￨" + tag for token in tokens]

## == BODY == ##

data = []

if LOAD:
# Loading from file (skip parsing)
	data = pickle.load(open(LOAD, "rb"))
	
else:
	for folder in os.scandir(DIR):
		# Iterates over folders, which correspond to languages, in HTML directory
		if os.path.basename(folder.name) in ["HGM"]: # langs w/o transcriptions
			continue
		for file in os.scandir(folder.path):
			#print(file.path)
			transcripts = get_transcripts(file)
			if transcripts != None:
				data.extend([(transcript, os.path.basename(file.name).split("_")[0].upper()) for transcript in transcripts])
	if SAVE:
		pickle.dump(data, open(SAVE, "wb"))
	

for (transcript, tag) in data:
	tokens = tokenize(transcript, tag) # Tokenize
	tokens_tagged = add_tags(tokens, tag) # Add tags to each token
				
	# Print tokens separated by space			
	print(" ".join(tokens_tagged))
