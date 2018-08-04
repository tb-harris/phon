# https://github.com/ucdaviscl/soliloquy_variation/blob/master/wordvecutil.py
# wordvecutil: Basic operations for word vectors
#  - loading, cosine similarity, nearest neighbors
#
# modified to work with opennmt format

import numpy
import sys
import getopt
import math

import sklearn.cluster
import sklearn.manifold
from matplotlib import pyplot

import pickle
NAMES = None
FAMILIES = None
COUNTS = None
MIN_COUNT = 0

def generate_colors(n):
    '''
    Generates a relatively even distribution
    of n colors in rgb format (r, g, b) where
    0 <= r, g, b <= 1; excludes white, black
    '''
    colors = []
    
    options = math.ceil((n + 2)**(1/3))
    r = range(options)
    
    #return [(i/options, j/options, k/options) for i in r for j in r for k in r if ((i != 0 or j != 0 or k != 0) and (i != 1 or j != 1 or k != 1))][0::(options**3)//n][:n]

    rgb256 = [(230, 25, 75), (60, 180, 75), (0, 130, 200), (245, 130, 48), (145, 30, 180), (240, 50, 230), (210, 245, 60), (250, 190, 190), (0, 128, 128), (170, 110, 40), (128, 0, 0), (170, 255, 195), (70, 240, 240), (128, 128, 0), (0, 0, 128), (255, 215, 180), (230, 190, 255)][:n]
    return [(r/256, g/256, b/256) for (r, g, b) in rgb256]

class word_vectors:

    # fname: the file containing word vectors in text format
    # maxtypes: the maximum size of the vocabulary

    def __init__(self, fname, maxtypes=0):
        self.word2idx = {}
        self.idx2word = []
        self.numtypes = 0
        self.dim = 0
        self.v = self.load_vectors(fname, maxtypes)

    # load vectors from a file in text format
    # fname: the file name
    
    def load_vectors(self, fname, max=0):
        cnt = 0
        with open(fname) as f:
            toks = f.readline().split()

            ##
            try: # Word2Vec Format
                if len(toks) != 2:
                    raise Exception
                numtypes = int(toks[0])
                dim = int(toks[1])
                
            except: # OpenNMT Format
                f.seek(0) # Returns to start of file
                dim = len(toks) - 1
                if COUNTS is not None:
                    numtypes = sum(1 for line in f if not COUNTS[line.split()[0]] < MIN_COUNT) # Counts lines in file, ignores vectors w/ below-min freq
                else:
                    numtypes = sum(1 for line in f)
                    
                print("Counted", numtypes, "types,", dim, "dimesions.")
                f.seek(0) # Returns to start of file
            ##
            
            if max > 0 and max < numtypes:
                numtypes = max

            # initialize the vectors as a two dimensional
            # numpy array. 
            vecs = numpy.zeros((numtypes, dim), dtype=numpy.float16)

            # go through the file line by line
            for line in f:
                # get the word and the vector as a string
                word, vecstr = line.split(' ', 1)
                vecstr = vecstr.rstrip()
                
                # excludes words below minimum count
                if COUNTS is not None and COUNTS[word] < MIN_COUNT:
                    continue

                # now make the vector a numpy array
                vec = numpy.fromstring(vecstr, numpy.float16, sep=' ')

                # add the normalized vector
                norm = numpy.linalg.norm(vec, ord=None)
                vecs[cnt] = vec/norm

                # index the word
                if not NAMES:
                    self.word2idx[word] = cnt
                    self.idx2word.append(word)
                else:
                    self.word2idx[NAMES[word]] = cnt
                    self.idx2word.append(NAMES[word])
            
                cnt += 1
                if cnt >= numtypes:
                    break
            
        return vecs

    # near gets the nearest neighbors of a word
    # target: target word or numpy array
    # numnear: number of nearest neighbors

    def near(self, target, numnear = 10):

        # check if string (instead of numpy array)
        if type(target) is str:
            # check if the word is in our index
            if target in self.word2idx:
                vector = self.v[self.word2idx[target]]
            else:
                return None
        else: # numpy array
            vector = target
            norm = numpy.linalg.norm(vector, ord=None)
            vector /= norm

        # get the distance to all the words we know.
        dist = self.v.dot(vector)

        # sort by distance
        near = sorted([(dist[i], self.idx2word[i]) for i in range(len(dist))], reverse=True)

        # trim results and return
        if numnear > len(near):
            numnear = len(near)
            
        return near[0:numnear]

    # sim returns the cosine similarity between two words.
    # because our vectors are normalized, we can just
    # use the dot product and we are done
    
    def sim(self, w1, w2):
        if not w1 in self.word2idx:
            return None
        if not w2 in self.word2idx:
            return None
        return self.v[self.word2idx[w1]].dot(self.v[self.word2idx[w2]])
        
        
    def analogy(self, positive, negative, n = 10):
    	'''
    	Returns n vectors most similar to
    		Σpositive - Σnegative
    	
    	Arguments:
    	* positive - list of words
    	* negative - list of words
    	
    	Return:
    	* vector info
    	'''
    	
    	# Get Σpositive - Σnegative
    	difference = sum([self.v[self.word2idx[w]] for w in positive]) - sum([self.v[self.word2idx[w]] for w in negative])
    	
    	return self.near(difference, n)
    
    
    def cluster(self, k):
        kmeans = sklearn.cluster.KMeans(n_clusters=k)
        
        # Compute clusters; membership = list of corresponding cluster IDs
        membership = kmeans.fit_predict(v.v)
        
        # Plot clusters
        self.plot(membership)
        
        # Build list of lists of vector labels within each centroid
        return [
            [self.idx2word[i] for i in range(len(membership)) if membership[i] == centroid]
            for centroid in range(k)]
    
    def plot(self, groups = []):
                
            
        mds = sklearn.manifold.MDS()
        
        # Performs dimensional scaling
        points = mds.fit_transform(self.v)
        
        if groups != []:
            colors = generate_colors(max(groups) - min(groups) + 1)
            color_list = [colors[group] for group in groups]
        elif FAMILIES: # Families -> colors
            families = [family for family in FAMILIES.keys() if len(FAMILIES[family]) > 1] # excludes 1-member families
            colors = generate_colors(len(FAMILIES))
            
            color_list = []
            for language in self.idx2word:
                for i, family in enumerate(families):
                    if language in FAMILIES[family]: # language in family
                        color_list.append(colors[i])
                        break
                    if i == len(families) - 1: # none found
                        color_list.append((0, 0, 0)) # No family found
        else:
            color_list = ["b"] * len(points)
                        
        # Plots points
        pyplot.scatter(
            [x for [x, y] in points], # x positions
            [y for [x, y] in points], # y positions
            color=color_list # colors
        )
            
            
        
        # Label each point with vector name
        for i, point in enumerate(points):
            pyplot.annotate(
                self.idx2word[i], # Label
                point # Coordinates
            )
        
        pyplot.show()
        
        return
    
    def get_family_counts(self, groups):
        for family, members in FAMILIES.items():
            print("\n\n" + family)
            for i, group in enumerate(groups):
                intersection = members & set(group) # Languages in both family and group
                print("Group", i, str(len(intersection)) + "\t" +
                      str(round(len(intersection)/len(group), 2)) + "\t" + # % of group in family
                      str(round(len(intersection)/len(FAMILIES[family]), 2)) # % of family in group
                     )
                print("\t", intersection)
        '''
        for i, group in enumerate(groups):
            print("\n\nCluster", i)
            for family, members in FAMILIES.items():
                num_members = len(members & set(group)) # Number of members of family in group
                print(family + "\t\t\t\t\t" + str(num_members) + "\t" +
                      str(round(num_members/len(group), 2)) + "\t" + # % of group in family
                      str(round(num_members/len(FAMILIES[family]), 2)) # % of family in group
                     )
        '''
        
        

# a sample drive
fname = ''
try:
    opts, args = getopt.getopt(sys.argv[1:], "hv:n:f:c:m:")
except getopt.GetoptError:
    print("word_vectors.py -v <word_vectors_txt>")
    sys.exit(1)
for opt, arg in opts:
    if opt == '-h':
        print("word_vectors.py -v <word_vectors_txt>")
        sys.exit()
    elif opt == '-v':
        fname = arg
    elif opt == '-n':
        NAMES = pickle.load(open(arg, "rb"))
    elif opt == '-f':
        FAMILIES = pickle.load(open(arg, "rb"))
    elif opt == '-c':
        COUNTS = {line.split()[0]: int(line.split()[2]) for line in open(arg, "r") if len(line.split()) >= 2}
    elif opt == '-m':
        MIN_COUNT = int(arg)
        

if fname == '':
    print("word_vectors.py -v <word_vectors_txt>")
    sys.exit()

print("Loading...")

# create the vectors from a file in text format,
# and load at most 100000 vectors
v = word_vectors(fname, 100000)
print("Done.")
