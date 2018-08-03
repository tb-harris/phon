# encoding: utf-8

'''
Normalizes, tokenizes, and tags phonetic transcriptions
from file to format suitable for processing by OpenNMT
File format: One transcription per line
	TAG⦀TRANSCRIPTION
'''

MIN_LENGTH = 2
#BAD_LANGUAGE = {"proto", "esperanto", "ido", "lojban", "interlingua", "volap", "toki", "translingual"} # excludes constructed, reconstructed
BAD_LANGUAGE = {"old", "middle", "classical", "gothic", "proto", "esperanto", "ido", "lojban", "interlingua", "volap", "toki", "translingual"} # excludes constructed, reconstructed, extinct prior to documentation

# == Symbol Groups by Type ==
UNKNOWN_PHONEME = {
}
	
PHONATION = {
	"ʰ", # aspiration
	"ʱ", # breathy voice
	"̚" # unreleased stop
}

SECONDARY_ARTICULATION = {
	"ʷ", # labalized
	"ʲ", # palatalized
	"ˠ", # velarized
	"ˁ" # pharyngealized
}
	
NASALIZATION = {"̃"} # ã
	
LENGTH = {
	"̆", # ă Extra-short
	"ː", # long
	"ˑ" # half-long
}
	
VOWEL_OTHER = {
	
	"̜", # ̜a Less rounded
	"̹", # ̹a More rounded (13)
	"ᵝ" # rounded
}
	
SYLLABICITY = {
	"̍", # Syllabic
	"̯" # Non-syllabic
}
			
RELATIVE_ARTICULATION = {
	"̝", "̞", # Raised, lowered
	"̟", "̠", # Advancced, retracted
	"̤",  # ̈Centralized
	"̽" # Mid-centralized (3) DELETED
}
	
SYLLABIC = {"̩"} # ̩r
	
OTHER = {
	"̢" # Hook
}
	
LAMINAL = { # 63
	"̻" 
}

# == Tokenization/Normalization Action Symbol Groups ==
ATTACH = { # Append to previous token
	"̥", # ̥x voiceless
	"̧", # ̧c cedille
	"̪", # ̪t dental
	"ʼ" # ejective DELETED
} | SECONDARY_ARTICULATION

REPLACE = { # Key must be single character
	"!": "ǃ", # click
	":": "ː", # vowel length
	"ʇ": "ǀ", "ʖ": "ǁ", "ʗ": "ǃ",
	"̊": "̥", # Voicelessness
	"̈": "̤", # Centralization
	"̺": "̪", # Dental
	"‿": "͡", # Affricate
	"͜": "͡", # Affricate - sometimes reps dipthong - eliminate symbol entirely?
	"g": "ɡ",
	"ʴ": "˞", # rhotic
	"ˀ": "ʔ", # glottal stop
	"ᶑ": "ɗ", # voiced retroflex implosive (contested?) -> voiced alveolar implosive
	"˔": "̝", # raised
	# rhotic vowels ???????
	"ɚ": "əɹ",
	"ɝ": "əɹ", # ??
	# NOTE : Fix below if decide to include affricate tie
	"ʦ": "ts",
	"ʣ": "dz",
	"ʧ": "tʃ",
	"ʤ": "dʒ",
	"ʨ": "tɕ",
	"ʥ": "dʐ",
	"ɮ": "lʒ",
	"ƛ": "tɬ",
	"¢": "ts"
}

ELIMINATE = { # Eliminate entire transcription
	"_", "ƙ",
	"ƞ", "ȵ", # Alveo palatal (nasals) ?
	"ȶ",
	"ƶ",
	"̬", # ̬p voiced (used only 3 times in wiktionary data)
	"-" # prefix/suffix in wiktionary data
}

DELETE = { # Delete symbol
	"'", "ˈ", "ˌ", # Stress
	"°", 
	"*", "^", "·", "ı",
	".", # Syllable
	"1", "2", "3", "4", "5", "6", "7", "8", "9", # Tone
	"¹", "²", "³", "⁴", "⁵", "⁶", "⁸", 
	"˥", "˦", "˧", "˨", "˩",
	"ˢ", "ˣ", "ˡ", 
	"̂", "̄", "̋", "̌", "̏", "ˇ",    # â ā ̋a ̌a ̏a
	"↓", "↗", "↘", "ꜜ",
	"᷄", "᷅", "᷆", "᷇", "᷈", # Tone contour
	"́", "́", "̀", # á ́a à Stress
	"̘", "̙", # ̘a ̙a ATR, RTR
	"̣", # Dot
	"ᵇ", "ᵈ", "ᵊ", "ᵐ", "ᵑ",
	"ᶢ", # voiced retroflex click ?
	"ⁿ", # Nasal release (28)
	"͡", # Affrication tie - Chose to eliminate b/c of prevelance of unmarked affricates
	"̰", # unknown
	"͈", # Fortis
	"͍", # Labial spreading ???
	"ʳ", # r-coloring
	"̬", # voicing ?????
	"◌", # ????
	"˞",
	"̽", # Mid-centralized (3)
	"̪̥",
	"ʼ",
	"∅", "⁻", "⁓", "ᶣ", "˭", "ˤ", "͇"
} | PHONATION | NASALIZATION | LENGTH | VOWEL_OTHER | SYLLABICITY | RELATIVE_ARTICULATION | SYLLABIC | OTHER | LAMINAL | SECONDARY_ARTICULATION

DELETE_ALL_AFTER = { # Delete symbol and all following
	",", "~" # May be better to split into two transcriptions
}

ALLOW = { # Not in use
	"a", "b", "c", "d", "e", "f", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "æ", "ð", "ø", "ħ", "ŋ", "œ", "ƙ", "ƛ", "ƞ", "ƶ", "ǀ", "ǁ", "ǂ", "ǃ", "ȵ", "ȶ", "ɐ", "ɑ", "ɒ", "ɓ", "ɔ", "ɕ", "ɖ", "ɗ", "ɘ", "ə", "ɚ", "ɛ", "ɜ", "ɝ", "ɞ", "ɟ", "ɠ", "ɡ", "ɢ", "ɣ", "ɤ", "ɥ", "ɦ", "ɧ", "ɨ", "ɩ", "ɪ", "ɫ", "ɬ", "ɭ", "ɮ", "ɯ", "ɰ", "ɱ", "ɲ", "ɳ", "ɴ", "ɵ", "ɶ", "ɷ", "ɸ", "ɹ", "ɺ", "ɻ", "ɽ", "ɾ", "ɿ", "ʀ", "ʁ", "ʂ", "ʃ", "ʄ", "ʇ", "ʈ", "ʉ", "ʊ", "ʋ", "ʌ", "ʍ", "ʎ", "ʏ", "ʐ", "ʑ", "ʒ", "ʔ", "ʕ", "ʖ", "ʗ", "ʘ", "ʙ", "ʜ", "ʝ", "ʟ", "ʡ", "ʢ", "ʣ", "ʤ", "ʦ", "ʧ", "ʯ", "β", "θ", "λ", "χ", "а", "ч", "ҫ", "ӕ"
} | ATTACH

CAN_VOICELESS = {"l", "m", "n", "r", "w", "ɲ", "ɹ", "ɽ", "ɾ", "ʋ"}
	
	
	
# FIX: ɝ/ɚ separation; ɮ; r-coloring; look at Americanist transcriptions; distinctive features?
	

import sys
import collections
import unicodedata
import io

DELIMITER = "⦀" # Separates language name from transcription

if len(sys.argv) != 4:
	print("process.py load save min_count")
	sys.exit()
	
LOAD = sys.argv[1]
SAVE = sys.argv[2]
LANG_MIN = int(sys.argv[3])

def unique(l):
	'''
	Removes duplicates from list of tokens/tags
	
	Arguments:
	* l: list of (list, string) doubles
	
	Return:
	* List without duplicates
	'''
	seen = dict()
	result = []
	
	for (tokens, tag) in l:
		word = "".join(tokens)
		if (word, tag) not in seen:
			seen[(word, tag)] = 1
			result.append((tokens, tag))
			
	return result

def normalize(x):
	string = x
	
	# Normalization options: NFD = decompose, NFC = decompose + combine
	# Do not use NFKD/NFKC - results in information loss (eg aspiration -> standard h)
	string = unicodedata.normalize("NFD", string)
	
	string = "".join(" " if c.isspace() else c for c in string) # Normalize spaces
	string = "".join(REPLACE[c] if c in REPLACE.keys() else c for c in string)  # Replace characters
	#string = "".join(c for c in string if c not in DELETE) # Delete characters in DELETE # MOVED TO TOKENIZE
	
	for c in ELIMINATE:
		if c in string:
			string = ""
	
	for i, c in enumerate(DELETE_ALL_AFTER):
		if c in string:
			string = string[:i]
			break
	
	return string

def count_tokens(tokens, counter):
	'''
	Increments counter for tokens in list
	Arguments:
	* tokens - list of tokens
	* counter - systems.Counter() object
	'''
	
	for token in tokens:
		counter[token] += 1

def read_transcriptions(f):
	'''
	Reads tagged transcriptions from text file formatted:
		tag⦀transcription
	Removes languages containing phrases in BAD_LANAGUAGES
	set, empty transcriptions.
	
	Return:
	* List of pairs (language, transcription)
	'''
	data = []
	
	for line in f:
		
		# Split line by delimiter
		parse = line.split(DELIMITER)
		
		# Get language, check if excluded
		lang = parse[0]
		if any(substring.lower() in lang.lower() for substring in BAD_LANGUAGE):
			continue
		
		# Normalize transcription
		transcription = normalize(parse[1])
		
		if transcription == "":
			continue
		
		# Append (language, transcription) pair
		data.append((lang, transcription))
		
	return data

def tokenize(transcription, tag):
	'''
	Splits transcription into symbols, adds
	start/end symbols.
	
	Arguments:
	* transcription - String to tokenize
	* tag - 3-letter language tag
	
	Return:
	* list of tokens
	'''
	
	in_paren = False
	deleted = True # Last character deleted or space
	
	tokens = []
	#tokens.append("#")
	for c in transcription:
		if c == "(" or (c == '\"' and not in_paren):
			in_paren = True
			deleted = True
		elif c == ")" or (c == '\"' and in_paren):
			in_paren = False
			deleted = True
		elif in_paren:
			deleted = True
		elif c in DELETE:
			deleted = True
		elif c.isspace():
			if len(tokens) > 0 and tokens[-1] != "#":
				tokens.append("#")
			deleted = True
		elif c == "/":
			break
		elif c == "|" and tag == "YEY": # YEY: | used like /
			break
		elif c in ["|", "[", "]"]:
			deleted = True
			continue
		elif c in ATTACH:
			if not deleted and len(tokens) > 0 and tokens[-1] != "#":
				if c == "̥" and tokens[-1][0] not in CAN_VOICELESS: # checks to make sure voicelessness marker can attach
					continue
				if c == tokens[-1][-1]: # skips duplicate markers
					continue
				tokens[-1] += c
		else:
			tokens.append(c)
			deleted = False
	
	if len(tokens) != 0 and tokens[-1] == "#":
		tokens.pop()
		
	#tokens = [token for token in tokens if token in ALLOW]
	if len(tokens) >= MIN_LENGTH:
		return tokens
	else:
		return []

def add_tag(tokens, tag):
	'''
	Appends "￨" (OpenNMT feature delimiter)
	followed by tag to each element in list
	
	Arguments:
	* tokens - List of elements to be tagged
	* tag - Tag to append to elements
	
	Return:
	* Tagged list
	'''
	return [token + "￨" + tag.replace(" ", "") for token in tokens if len(tokens) >= MIN_LENGTH]

token_counts = collections.Counter()
tag_counts = collections.Counter() # Counts numbers of valid transcripts with each language tag
f = io.open(SAVE, "w", encoding="utf-8")

# Gets tags, transcriptions from file
data = read_transcriptions(io.open(LOAD, "r", encoding="utf-8"))
data_processed = []

for (tag, transcriptions) in data:
	for transcription in transcriptions.split(): # Splits transcriptions w/ spaces
		tokens = tokenize(transcription, tag)
		if tokens != []:
			data_processed.append((tokens, tag))
			
# Exclude duplicates
#data_processed = [element for i, element in enumerate(data_processed) if element not in data_processed[:i]]
data_processed = unique(data_processed)

for (tokens, tag) in data_processed:
	count_tokens(tokens, token_counts)
	tag_counts[tag] += 1 # Increments language count

langs_allowed = {lang for lang, count in tag_counts.items() if count >= LANG_MIN}

for (tokens, tag) in data_processed:
	if tag in langs_allowed:
		tokens_tagged = add_tag(tokens, tag)
		f.write(" ".join(tokens_tagged) + "\n")
	
for token in sorted(token_counts.keys()):
	print((token + "\t" + str(token_counts[token])).encode('utf-8'))
	
print("Total Tokens:", len(token_counts))
print("Total Languages:", len(langs_allowed))
