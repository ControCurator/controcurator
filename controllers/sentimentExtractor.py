#
# Sentiment analysis on text
#
import nltk
from nltk.corpus import stopwords
from nltk.tree import *
from nltk.corpus import sentiwordnet as swn

class SentimentExtractor():

	@staticmethod
	def getSentiment(text):
		sentences = nltk.sent_tokenize(text)
		s = {}
		s['sentences'] = len(sentences)
		s['words'] = 0
		s['sentiment'] = 0
		s['positivity'] = 0
		s['negativity'] = 0
		s['intensity'] = 0
		
		for sentence in sentences:
			if sentence <> '.':
				sentence = sentence.replace(' .', '.')
		
				tagged = nltk.pos_tag(nltk.word_tokenize(sentence))
				for word, treebank in tagged:
					sentiment = SentimentExtractor.get_sentiment_score_from_tagged(word, treebank, skipWordNetPos=[])
					if sentiment <> None and sentiment[0] != 0 and sentiment[1] != 0:
						s['words'] += 1
						s['positivity'] += sentiment[0]
						s['negativity'] += sentiment[1]
						s['sentiment'] = (s['positivity'] - s['negativity']) / s['words']
						s['intensity'] = (s['positivity'] + s['negativity']) / s['words']
		return s


	@staticmethod
	# get the sentiment values of the tagged entities
	def get_sentiment_score_from_tagged(token, treebank, skipWordNetPos=[]):
	    wordnet_pos = SentimentExtractor.treebank_to_wordnet_pos(treebank, skipWordNetPos)
	    if wordnet_pos: # only print matches
	        senti_synsets = list(swn.senti_synsets(token, wordnet_pos))
	        if senti_synsets:
	            return senti_synsets[0].pos_score(), senti_synsets[0].neg_score()

	@staticmethod
	# translates the treebank to the wordnet POS tags
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


