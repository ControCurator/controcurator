import nltk
from nltk.corpus import stopwords
from nltk.tree import *
from elasticsearch import Elasticsearch
from esengine import Document, StringField
from nltk.corpus import sentiwordnet as swn
import string
from pprint import pprint
import justext
import time
import datetime

def print_r(the_object):
    print ("CLASS: ", the_object.__class__.__name__, " (BASE CLASS: ", the_object.__class__.__bases__,")")
    pprint(vars(the_object))

es = Elasticsearch(['http://controcurator.org/ess/'], port=80)
stop = stopwords.words('english') + list(string.punctuation)

INDEX  = 'anchors'
TYPES = 'vaccination'
LOGDEX = 'crowdylog'


# NP patterns   
pattern = r"""
  NP: {<DT|JJ|NN.*>+}          # Chunk sequences of DT, JJ, NN
  PP: {<IN><NP>}               # Chunk prepositions followed by NP
  VP: {<VB.*><NP|PP|CLAUSE>+$} # Chunk verbs and their arguments
  CLAUSE: {<NP><VP>}           # Chunk NP, VP
  """ # define a tag pattern of an NP chunk
NPChunker = nltk.RegexpParser(pattern) # create a chunk parser
anchors = []

# An anchor is an entity for which we measure controversy
# This can be for instance a noun phrase, a named entity, a sentence
# Anchors are stored in the anchors index, whith their seed as document type (e.g. 'vaccination')
# Each instance of an anchor is cached in an anchor entity
class Anchor(Document):

	_es = Elasticsearch(['http://controcurator.org/ess/'], port=80)
	_index = "anchors"  # optional, it can be set after using "having" method
	_doctype = "vaccination"  # optional, it can be set after using "having" method

	# the current time
	now = lambda: datetime.datetime.utcnow().isoformat()

	# initiate a new anchor
	# set existing anchor if it is in the database
	@staticmethod
	def add(seed, key, label, instance):

		# check if this anchor exists
		anchor = Anchor.exists(seed, key)
		if(anchor):
			self = anchor
		else:
			# new anchor
			self = Anchor.create()
			self.key = key
			self.label = label
			self.instances = []
			self.count = 0
			self.positive = 0
			self.negative = 0
			self.controversy = 0
			self.created = self.now
			self.updated = self.now
			self.addInstance(instance)
			self.updateCache()

	@staticmethod
	def exists(seed, key):
		try:
			anchor = Anchor.get(id=key)
			print anchor
			return anchor
		except:
			return False



	def children(self):
		# Return documents that this anchor appears in
		return {}


	def addInstance(self, instance):
		# adds this instance to the cache of the anchor
		self.count += 1
		self.instances.append(instance)
	
	def updateCache(self):
		# aggregate all instances in the anchor cache
		self.sentiment = 0.5

	def firstInstance(self):
		return 'first'

	def lastInstance(self):
		return 'last'


def ExtractPhrases( myTree, phrase):
    myPhrases = []
    if (myTree.label()==phrase):
        myPhrases.append( myTree.copy(True) )
    for child in myTree:
        if (type(child) is Tree):
            list_of_phrases = ExtractPhrases(child, phrase)
            if (len(list_of_phrases) > 0):
                myPhrases.extend(list_of_phrases)
    return myPhrases




def treebank_to_wordnet_pos(treebank, skipWordNetPos=[]):
    if "NN" in treebank and "n" not in skipWordNetPos: # singular and plural nouns (NN, NNS)
        return "n"
    elif "JJ" in treebank and "a" not in skipWordNetPos: # adjectives including comparatives and superlatives (JJ, JJR, JJS)
        return "a" 
    elif "VB" in treebank and "v" not in skipWordNetPos: # verbs in various forms (VB, VBD, VBG, VBN, VBP, VBZ)
        return "v"
    elif "RB" in treebank and "r" not in skipWordNetPos: # adverbs including comparatives and superlatives (RB, RBR, RBS)
        return "r"
    # if we don't match any of these we implicitly return None

def get_sentiment_score_from_tagged(token, treebank, skipWordNetPos=[]):
    wordnet_pos = treebank_to_wordnet_pos(treebank, skipWordNetPos)
    if wordnet_pos: # only print matches
        senti_synsets = list(swn.senti_synsets(token, wordnet_pos))
        if senti_synsets:
            return senti_synsets[0].pos_score() - senti_synsets[0].neg_score()

def getText(document):
	paragraphs = justext.justext(document, justext.get_stoplist("English"))
	return ''.join(paragraph.text for paragraph in paragraphs)


def getTagged(text):
	tagged = []
	sentences = nltk.sent_tokenize(text) # NLTK default sentence segmenter
	words = [nltk.word_tokenize(sent) for sent in sentences]
	tagged = [nltk.pos_tag(word) for word in words]
	return tagged


def getNPs(tagged):

    # noun phrase identification
    chunks = NPChunker.parse(tagged)
    nps = []
    list_of_noun_phrases = ExtractPhrases(chunks, 'NP')
    for np in list_of_noun_phrases:
        if(not (len(np) == 1 and np[0][0] in stop)):
            #key = " ".join(word+"/"+tag for word, tag in np)
            key = " ".join(word for word, tag in np)
            nps.append(key)
    return nps

def getSentiment(tagged):
	sentiment = {'count':0,'score':0,'positive':0,'negative':0,'intensity':0,'positive_words':[],'negative_words':[]}
	for word, treebank in tagged:
		score = get_sentiment_score_from_tagged(word, treebank, skipWordNetPos=[])
		if score:
			sentiment['count'] += 1
			sentiment['score'] += score
			if score > 0:
				sentiment['positive'] += score
				sentiment['positive_words'].append(word)
			else:
				sentiment['negative'] += score
				sentiment['negative_words'].append(word)
				sentiment['intensity'] = sentiment['positive'] + (-1 * sentiment['negative'])
	return sentiment

def addBulk(anchors):
	bulk_data = [] 
	for child in anchors:
		data_dict = {}
		for i in anchors[child]:
			data_dict[i] = anchors[child][i]

		op_dict = {
			"create": {
				"_index": INDEX, 
				"_type": TYPES, 
				"_id": hash(anchors[child]['topic']+anchors[child]['parent'])
			}
		}
		bulk_data.append(op_dict)
		bulk_data.append(data_dict)

	#pprint(bulk_data)
	res = es.bulk(index = INDEX, body = bulk_data)

if __name__=='__main__':

	query = {
	    "query" : {
	        "bool" : { 
	            "must_not" : {
	                "term" : { 
	                    "tagged" : True
	                }
	            }
	        }
	    },
		"size": 10,
	}

	response= es.search(index="crowdynews", body=query)

	for hit in response["hits"]["hits"]:
		if 'text' in hit['_source']:
			doc = hit['_source']['text']
		elif 'title' in hit['_source']:
			doc = hit['_source']['title']
		else:
			continue

		if len(doc) == 0:
			continue

		anchor = Anchor.add('vaccination','needle','Needle','doc1')
		anchor = Anchor.add('vaccination','autism','Autism','doc2')
		anchor = Anchor.add('vaccination','needle','Needle','doc2')
		print_r(anchor)
		break

		#print doc
		text = getText(doc)
		#print text
		tagged = getTagged(text)
		#print tagged

		anchors = {}
		retrieved = now()
		# this should not occur, but just a safety check
		if 'retrieved' not in hit['_source']:
			continue
		date = hit['_source']['retrieved']
		if 'date' in hit['_source']:
			date = hit['_source']['date']

		for sentence in tagged:

			sentiment = getSentiment(sentence)
			#print sentiment
#			sentenceTopics = getTopics(sentence)
#			for t in sentenceTopics:
#				if t.lower() not in stop:
#					if t not in topics:
#						topics[t] = {'topic':t,'type':'NOUN','date':date,'retrieved':retrieved,'parent':hit['_id'],'service':hit['_type'],'count':0,'words':0,'positive':0,'negative':0,'intensity':0,'controversy':0}
#					topics[t]['count'] += 1
#					topics[t]['words'] += sentiment['count']
#					topics[t]['positive'] += sentiment['positive']
#					topics[t]['negative'] += sentiment['negative']
#					topics[t]['intensity'] = topics[t]['positive'] + (-1 * topics[t]['negative'])
#					topics[t]['controversy'] = topics[t]['intensity'] / max(abs(topics[t]['positive'] - (-1 * topics[t]['negative'])),1)
		
			for chunk in nltk.ne_chunk(sentence):
				if type(chunk) is nltk.Tree:
					t = ' '.join(c[0] for c in chunk.leaves())
					cat = chunk.label()
#					print t,cat
					if t not in topics:
						topics[t] = {'topic':t,'type':cat,'date':date,'retrieved':retrieved,'parent':hit['_id'],'service':hit['_type'],'count':0,'words':0,'positive':0,'negative':0,'intensity':0,'controversy':0}

					if t in topics:
						topics[t]['type'] = cat
					topics[t]['count'] += 1
					topics[t]['words'] += sentiment['count']
					topics[t]['positive'] += sentiment['positive']
					topics[t]['negative'] += sentiment['negative']
					topics[t]['intensity'] = topics[t]['positive'] + (-1 * topics[t]['negative'])
					topics[t]['controversy'] = topics[t]['intensity'] / max(abs(topics[t]['positive'] - (-1 * topics[t]['negative'])),1)


		if topics:
#			for t in topics:
				#print t+' - '+topics[t]['type']
			addBulk(topics)
		es.update(index = hit['_index'], doc_type=hit['_type'], id=hit['_id'], body = {'doc':{'tagged' : True}})
		#break
	#pprint(topics)