import json
import sys
import nltk
from lxml import html
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import word_tokenize
import re
import os
print os.getcwd()

class Preprocess_topic_data(object):

	def preprocess_text(self,data):
		#print os.getcwd()
		raw_text = []
		t_id = []
		
		
		#d = json.load(data)
		for entry in data:
			text = entry['_source']['document']['text']
			idx = entry['_id']
			#print text,idx
			paragraphs = self.extract_paragraphs(text)
			lemmatized_paragraphs = self.lemmatization(paragraphs)

			raw_text.append(lemmatized_paragraphs)
			t_id.append(str(idx))
		return t_id, raw_text




	def extract_paragraphs(self,text):
		extract_paragraphs =''
		pattern = re.compile(r"(<p>(.*?)</p>)")
		matches = re.search(pattern,text)
		search_obj = pattern.findall(text)
		
		extract_paragraphs += '0 '
		for entry in search_obj:
			paragraph = (str(entry[1]))
			extract_paragraphs += paragraph

		return extract_paragraphs

	def lemmatization(self,text):
		tokens = word_tokenize(text)
		
		lmtzr = WordNetLemmatizer()
		lemmas = [lmtzr.lemmatize(word)
					for word in tokens]
		text = " ".join(lemmas)
		
		return text

def main(Article):
	#data = "../data/documents_output.json"
	data = Article

	Preprocess = Preprocess_topic_data()
	TopicID, Topic_text = Preprocess.preprocess_text(data)
	#Preprocess.lemmatization(data)
	return TopicID, Topic_text

if __name__ == '__main__':
	main("This is a piece of text, words churches dogs are tokenized than lemmatization is performed")