from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction import text 
from sklearn.externals import joblib
import collections
import json
import pprint
import pickle
import os
import sys
import numpy as np
import process

np.set_printoptions(threshold=np.nan)

article_nr = 0

Topicdict= collections.defaultdict(list)

def print_top_words(model, feature_names, n_top_words):
		    for topic_idx, topic in enumerate(model.components_):
		        print("Topic #%d:" % topic_idx)
		        print(" ".join([feature_names[i]
		                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
		    print()

def top_words(model, feature_names, n_top_words):
	topic_word = []
	for topic_idx, topic in enumerate(model.components_):
		feat = " ".join([feature_names[i] + ' ' + str(round(topic[i],2))
		                        for i in topic.argsort()[:-n_top_words - 1:-1]])
		a = (topic_idx, feat)

		topic_word.append(a)
		
	return topic_word

def top_words2(model, feature_names, n_top_words):
	topic_word = []
	for topic_idx, topic in enumerate(model.components_):
		feat = ([feature_names[i] 
		        	for i in topic.argsort()[:-n_top_words - 1:-1]])
		a = (topic_idx, feat)

		topic_word.append(a)
			
	return topic_word

def top_name(model, feature_names, ids,top_words):
	topic_name = []
	for i in ids:
		for j,k in top_words:
			if int(i) == int(j):
				topic_name.append(str(k[0]))
	return topic_name

def top_topics(dtm):
	top_n_topics = []
	nr_of_topics = -4
	max_topic_idx = np.argpartition(dtm, nr_of_topics)[nr_of_topics:]
	max_topic_values = dtm[max_topic_idx[nr_of_topics:]]

	a = np.reshape(max_topic_idx,4)
	b = np.reshape(max_topic_values,4)
	return a,b

def top_ids(dtm,lda,tf_feature_names,top_words,topic_id):
	global article_nr
	global topic_dict

	boolean = dtm > 0.2
	ids = np.argwhere(boolean)
	ids = ids.flatten()
	value = dtm[boolean]

	topic_term = top_name(lda,tf_feature_names,ids,top_words)

	#print list(ids), value, article_nr,topic_term
	add_to_dict(topic_id[article_nr],(list(ids)),value,topic_term)
	article_nr += 1
	#return list(ids), value)

def add_to_dict(keys,topic,value,topic_name):
	zipped = zip(topic_name,value)
	Topicdict[keys] = None
	dict_entry = []
	for i,j in zipped:
		a = i,float(round(j,2))
		dict_entry.append(a)

	Topicdict[keys] = dict_entry
	#print zipped


def main(json):
	n_top_words = 1
	TopicID, corpus = process.main(json)
	#print TopicID
	with open('../models/LDA/vectorizer.pkl', 'rb') as fin:
	  	count_vect = pickle.load(fin)

	lda = joblib.load('../models/LDA/lda.pkl') 

	dtm = count_vect.transform(corpus)
	tf_feature_names = count_vect.get_feature_names()

	'''DOCUMENT TERM DISTRIBUTION (MATRIX)'''
	doc_topic_dist_unnormalized = np.matrix(lda.transform(dtm))
	doc_topic_dist = doc_topic_dist_unnormalized/doc_topic_dist_unnormalized.sum(axis=1)
	
	'''GET TOPICS TERMS'''
	A = np.asarray(doc_topic_dist)
	t_words = top_words2(lda,tf_feature_names,n_top_words)
	'''GET TOPICS ABOVE THRESHOLD'''
	np.apply_along_axis(top_ids,1,A,lda,tf_feature_names,t_words,TopicID)

	'''Dictionary: Key: article ID, Value: (Topic(most relevant term) + Topic score)'''
	#print Topicdict['57f3ba42e4b05e7633c585e8']
	#print Topicdict['57f34be1e4b01506cbf24f39']


	with open('../models/LDA/Topic_dict.pkl', 'wb') as Tdict:
		pickle.dump(Topicdict,Tdict)

	return Topicdict


if __name__ == '__main__':
	main()