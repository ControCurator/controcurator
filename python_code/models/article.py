import nltk
from nltk.corpus import stopwords
from nltk.tree import *
from nltk.corpus import sentiwordnet as swn
import justext
import string
from pprint import pprint
from elasticsearch import Elasticsearch
import re
import pandas as pd
from esengine import Document, StringField, IntegerField, FloatField, DateField, ArrayField, ObjectField

from anchor import *

# Primitive Feature Extration
# abstract class that extracts primitive features for a given document
# these features are stored as a cache in the document

stop = stopwords.words('english') + list(string.punctuation)

# NP patterns   
pattern = r"""
  NP: {<DT|JJ|NN.*>+}          # Chunk sequences of DT, JJ, NN
  PP: {<IN><NP>}               # Chunk prepositions followed by NP
  VP: {<VB.*><NP|PP|CLAUSE>+$} # Chunk verbs and their arguments
  CLAUSE: {<NP><VP>}           # Chunk NP, VP
  """ # define a tag pattern of an NP chunk
NPChunker = nltk.RegexpParser(pattern) # create a chunk parser

es = Elasticsearch(['http://controcurator.org/ess/'], port=80)



# Articles are any kind of document


class Article(Document):

	_es = Elasticsearch(['http://controcurator.org/ess/'], port=80)
	_index = "controcurator"  # optional, it can be set after using "having" method
	_doctype = "article"

	id = StringField()
	features = ObjectField()
	url = StringField()
	author = ObjectField()
	title = StringField()
	text = StringField()
	sentences = ArrayField()
	entities = ObjectField()
	service = StringField()

	published = DateField()
	retrieved = DateField()
	children = ArrayField()
	parent = StringField()

	def getTexts(self):
		# get the content of the instance by combining the title and text
		texts = []
#		print self.text
#		if hasattr(self, 'title'):
#			texts.append(self.title)
		if hasattr(self, 'text'):
			texts.append(self.text)
		return texts

	def verifyLanguage(self, texts):
		# verify that the text contains only western characters
		# otherwise the document is ignored
		if texts[0] == None:
			raise ValueError('The document has no text')
		if all(ord(c) < 128 for c in ' '.join(texts[:1])):
			raise ValueError('The document contains illegal characters')

	def cleanTexts(self, texts):
		texts = [text.replace('\n',' ') for text in texts]
		texts = [re.sub(r'http\S+', '', text) for text in texts]
		texts = [text.strip() for text in texts]

		return texts


	def getParagraphs(self, texts):
		# get the paragraphs in a text
		paragraphs = []
		[paragraphs.extend(justext.justext(text, justext.get_stoplist("English"))) for text in texts]
		return [paragraph.text for paragraph in paragraphs]

	def getSentences(self, texts):
		sentences = []
		[sentences.extend(nltk.sent_tokenize(text)) for text in texts]
		return [sentence.replace(' .', '.') for sentence in sentences if sentence <> '.']

	def getEntities(self, sentences):
		# get all named entities and their sentiment
		entities = {}
		for i in range(len(sentences)):
			sentence = Sentence(sentences[i])
			# POS tag this sentence

			sentiment = sentence.getSentiment()
			
			sentenceEntities = sentence.getNamedEntities()
			#sentenceEntities.update(sentence.getNounPhrases())

			for entity in sentenceEntities:
				e = entity.replace(' ', '_').lower()
				if e not in entities:
					entities[e] = {}
				if i not in entities[e]:
					entities[e][i] = {}
				entities[e][i]['label'] = entity
				entities[e][i]['type'] = sentenceEntities[entity]
				entities[e][i]['sentiment'] = sentiment

				a = Anchor.getOrCreate(entity)
				a.addInstance(self.id, i, sentiment)
				#print 'Instance',self.id,i,entity
				a.save()

		return entities


	def updateFeatures(self):


		#hasAuthor : boolean
		#hasTitle : boolean
		try:
			texts = self.getTexts()
			self.verifyLanguage(texts)
			texts = self.cleanTexts(texts)
	#		print self.text
		except:
			texts = []


		paragraphs = self.getParagraphs(texts)
#		pprint(self.paragraphs)
		sentences = self.getSentences(paragraphs)

		# store the sentences so that we can reference to them and make easy summarizations
		self.sentences = sentences
		if len(sentences) == 0:
			raise ValueError('Article has no sentences')

#		pprint(self.sentences)
#		self.sentiment = aggregateSentiment(sentences)
		entities = self.getEntities(sentences)
		self.entities = entities

		features = {}
		features['paragraphs'] = len(paragraphs)
		features['sentences'] = len(sentences)
		features['entities'] = len(entities)
		features['characters'] = sum([len(text) for text in texts])

		df = pd.DataFrame([entities[e][s]['sentiment'] for e in entities for s in entities[e]])
		mean = df.mean()
		total = df.sum()
		features.update({'mean_'+k:v for k, v in mean.iteritems()})
		features.update({'total_'+k:v for k, v in total.iteritems()})
		print '-UPDATED',self.id
		self.features = features


	def getFeatures(self):
		if len(self.features) == 0:
			self.updateFeatures()
		return self.features

	def getJSON(self):
		# returns JSON safe dict of the article
		# this is needed to avoid issues with timestamps
		return self._values



#
# Sentiment of a sentence
#
class Sentence():

	def __init__(self, sentence):
		self.tagged = nltk.pos_tag(nltk.word_tokenize(sentence))


	def getTagged(self, sentence):
		# get POS tags of the text
		words = nltk.word_tokenize(sentence)
		tagged = nltk.pos_tag(words)
		return tagged

	def ExtractNounPhrases(self, myTree, phrase):
	    myPhrases = []
	    if (myTree.label()==phrase):
	        myPhrases.append( myTree.copy(True) )
	    for child in myTree:
	        if (type(child) is Tree):
	            list_of_phrases = self.ExtractNounPhrases(child, phrase)
	            if (len(list_of_phrases) > 0):
	                myPhrases.extend(list_of_phrases)
	    return myPhrases

	def getNounPhrases(self):

	    # noun phrase identification
	    chunks = NPChunker.parse(self.tagged)
	    nps = {}
	    list_of_noun_phrases = self.ExtractNounPhrases(chunks, 'NP')
	    for np in list_of_noun_phrases:
	        if(not (len(np) == 1 and np[0][0] in stop)):
	            #key = " ".join(word+"/"+tag for word, tag in np)
	            key = " ".join(word for word, tag in np)
	            nps[key] = 'NP'
	    return nps

	def getNamedEntities(self):
		entities = {}
		chunks = nltk.ne_chunk(self.tagged)
		for chunk in chunks:
			if type(chunk) is nltk.Tree:
				t = ' '.join(c[0] for c in chunk.leaves())
				cat = chunk.label()
				entities[t] = cat
		return entities

	def getSentiment(self):
		sentiment = {'words':0,'score':0,'positivity':0,'negativity':0,'intensity':0}
		for word, treebank in self.tagged:
			score = self.get_sentiment_score_from_tagged(word, treebank, skipWordNetPos=[])
			if score:
				sentiment['words'] += 1
				sentiment['score'] += score
				if score > 0:
					sentiment['positivity'] += score
				else:
					sentiment['negativity'] += score
					sentiment['intensity'] = sentiment['positivity'] + (-1 * sentiment['negativity'])
		return sentiment

	# get the sentiment values of the tagged entities
	def get_sentiment_score_from_tagged(self, token, treebank, skipWordNetPos=[]):
	    wordnet_pos = self.treebank_to_wordnet_pos(treebank, skipWordNetPos)
	    if wordnet_pos: # only print matches
	        senti_synsets = list(swn.senti_synsets(token, wordnet_pos))
	        if senti_synsets:
	            return senti_synsets[0].pos_score() - senti_synsets[0].neg_score()

	# translates the treebank to the wordnet POS tags
	def treebank_to_wordnet_pos(self, treebank, skipWordNetPos=[]):
	    if "NN" in treebank and "n" not in skipWordNetPos: # singular and plural nouns (NN, NNS)
	        return "n"
	    elif "JJ" in treebank and "a" not in skipWordNetPos: # adjectives including comparatives and superlatives (JJ, JJR, JJS)
	        return "a" 
	    elif "VB" in treebank and "v" not in skipWordNetPos: # verbs in various forms (VB, VBD, VBG, VBN, VBP, VBZ)
	        return "v"
	    elif "RB" in treebank and "r" not in skipWordNetPos: # adverbs including comparatives and superlatives (RB, RBR, RBS)
	        return "r"
	    # if we don't match any of these we implicitly return None





