from __future__ import print_function
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction import text 
from sklearn.externals import joblib
from sklearn import metrics

import pyLDAvis
import pyLDAvis.sklearn
import json
import pprint
import pickle
import os
import sys
import numpy as np
import csv
np.set_printoptions(threshold=np.nan)


import process

class LDA:
	def __init__(self, raw_files, n_topics, n_iterations, alpha, beta):

		self.extra_stop_words = ['guim','gu','image__caption','jpg','html','element','span','https','http','href','em','www','com','class','br',
	                        	'ul','theguardian','2016','2017','title','h1','h2','style','width','font','height','li','lt','quot','gt','said',
	                        	'strong','td','url','id','img','figcaption','figure','src','year','years','new','just','like','im']

		self.stop_words = text.ENGLISH_STOP_WORDS.union(self.extra_stop_words)

		self.count_vect = CountVectorizer(lowercase = True,
									strip_accents = 'unicode',
									input='content',
									stop_words=self.stop_words,
			                        max_df = 0.3, 
			                        min_df = 0.01)
		self.n_topics = n_topics
		self.raw_files = raw_files
		self.n_iterations = n_iterations
		self.alpha = alpha
		self.beta = beta

		self.lda = LatentDirichletAllocation(n_topics = self.n_topics,
											learning_method ='batch',
											doc_topic_prior = self.alpha,
											topic_word_prior= self.beta,
											max_iter = self.n_iterations,
											random_state = 1
		                               		)

	def document_term_matrix(self,corpus):
		dtm = self.count_vect.fit_transform(corpus)
		return dtm

	def document_topic_dist(self,corpus,option):
		dtm_test = self.count_vect.transform(corpus)
		doc_topic_dist_unnormalized = np.matrix(self.lda.transform(dtm_test))
		doc_topic_dist = doc_topic_dist_unnormalized/doc_topic_dist_unnormalized.sum(axis=1)
		
		if option == 1:
			return doc_topic_dist.argmax(axis=1)
		else:
			return doc_topic_dist


	def extract_text(self):
		raw_text = []
		for doc in self.raw_files: 
			#print doc
			with open(doc) as json_file:
				d = json.load(json_file)
				text = d['response']['content']['blocks']['body'][0]['bodyHtml']
				raw_text.append(text)
		return raw_text	

	def feature_names(self):
		tf_feature_names = self.count_vect.get_feature_names()
		return tf_feature_names

	def fit(self,dtm):
		self.lda.fit(dtm)
		return self.lda


	def print_top_words(self, model, feature_names, n_top_words):
		    for topic_idx, topic in enumerate(model.components_):
		        print("Topic #%d:" % topic_idx)
		        print(" ".join([feature_names[i]
		                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
		    print()

	

def main(json):
	
	rootdir = '../models/data'
	filenames = []
	raw_text = []

	n_samples = 2000
	n_features = 1000
	
	n_iterations = 50
	n_topics = 50
	alpha = 0.3
	beta = 1.5


	n_top_words = 10
	clda = LDA(filenames, n_topics,n_iterations,alpha,beta)
	TopicID, corpus = process.main(json)

	dtm = clda.document_term_matrix(corpus)
	clda.fit(dtm)
	lda = clda.lda
	dtd = clda.document_topic_dist(corpus,0)
	Parameters = [n_iterations,n_topics,alpha,beta]
	Score = lda.score(dtm)
	#Silscore = metrics.silhouette_score(dtd,clda.feature_names,sample_size = 1000)

	lda_score = str([Parameters, int(Score)])


	tf_feature_names = clda.feature_names()
	clda.print_top_words(lda,tf_feature_names, n_top_words)
	#print(clda.document_topic_dist(corpus,0))

	
	np.set_printoptions(threshold=np.nan)


	with open('../models/LDA/lda_LogLikelihood.csv','ab') as csvfile:
		fieldnames = ['n_iterations','n_topics','alpha','beta','score']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writerow({'n_iterations':n_iterations,"n_topics":n_topics,'alpha':alpha,'beta':beta,'score':int(Score)})
		#writer.write('\n')

	with open('../models/LDA/vectorizer.pkl', 'wb') as vectdump:
  		pickle.dump((clda.count_vect), vectdump)

  	with open('../models/LDA/lda.pkl', 'wb') as ldadump:
  		pickle.dump((lda), ldadump)

	#joblib.dump(clda.lda,'../models/LDA/lda.pkl')



if __name__ == "__main__":
    main()