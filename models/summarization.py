import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time
import os
import json
import re
import collections
import nltk, pprint
from nltk.tree import *
import nltk.tag.stanford as st 
from collections import Counter
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
import numpy as np
#sys.path.insert(0, '..')
import os

###CHANGE PATH###
Classifier_Stanfordpath = ""
Ner_Stanfordpath = ""

java_path = "C:\Program Files\Java\jre1.8.0_101/bin/java.exe"

os.environ['JAVAHOME'] = java_path


tagger = st.StanfordNERTagger(Classifier_Stanfordpath, Ner_Stanfordpath)

##EXAMPLE PATH LOCATION###
#tagger = st.StanfordNERTagger('C:\Users\A\Documents\MASTERPROJECT\Controcurator_master\models\LDA\stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz','C:\Users\A\Documents\MASTERPROJECT\Controcurator_master\models\LDA/stanford-ner/stanford-ner-3.7.0.jar')


import elasticsearch
from elasticsearch import Elasticsearch, ConnectionTimeout,helpers

es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80,timeout=240)


def get_data():
    query = {
          "query": {
            "bool": {
              "must": [
                
                
              ]
            }
          },
          "from": 1,
          "size": 1,
          "sort": [],
          "aggs": {}
        }

    response = es.search(index="controcurator", doc_type="article", body=query)
    data = response['hits']['hits']
    return data

def extract_comments(article):
    comments = article['_source']['comments']
    return comments

def get_sentiment(comment):

    positive = comment['sentiment']['positivity']
    negative = comment['sentiment']['negativity']

    return positive, negative

def get_topics(article):
    topics = article['_source']['features']['topics']
    return topics

def extract_text(comment):
    body = comment['text']
    sentences = nltk.word_tokenize(body)
    return sentences

def extract_nltk(comment):
    body = comment['text']
    entities = {}
    sentences = nltk.sent_tokenize(body)
    print(sentences)
    for sentence in sentences:

        words = nltk.word_tokenize(sentence)
        tagged = nltk.pos_tag(words)
        chunks = nltk.ne_chunk(tagged)
        for chunk in chunks:
            if type(chunk) is nltk.Tree:
              t = ''.join(c[0] for c in chunk.leaves())
              entities[t] = chunk.label()
    #print entities
    return entities

def named_entities(sentence):
    Nen = tagger.tag(sentence)
    return Nen

def get_entity(tagged_text,categories):
    ALL = []
    for word in tagged_text:
        for category in categories:
          if word[1] == category:
              #vars()[category].append(word)
              ALL.append(word)
    
    return ALL


def getArticleVector(article,categories):
      pos_sentiment = []
      neg_sentiment = []
      article_vector = {}
      raw_comments = extract_comments(article)
      topics = get_topics(article)
      
      tagged_comments = []

      for comment in raw_comments:
        if comment['reply-to'] == "":
          
          ###GET SENTIMENT##
          pos, neg = get_sentiment(comment)
          pos_sentiment.append(pos)
          neg_sentiment.append(neg)
          ###GET NAMED_ENTITIES##
          comment_id = comment['id']

          '''
          tagged_ntlk = extract_nltk(comment)
          print(tagged_ntlk)
          '''
          tagged_text = extract_text(comment)
          entities = named_entities(tagged_text)
          filter_entities = get_entity(entities, categories)
          count = Counter(filter_entities).items()
          
          article_vector[comment_id] = count
          
      
      return article_vector.items()

    
def NER(corpus,categories):

  NE_dict = {}
  for article in corpus:
    start_time = time.time()
    NER_count = getArticleVector(article,categories)
    #print article
    output = []
    idx = str(article["_id"])

    for ids, entities in NER_count:
      b = []
      for entity, count in entities:
        a = {}
        a["name"] = entity[0]
        a["value"] = count
        a["label"] = entity[1]
        b.append(a)

      output.append(b)
    end_time = time.time()
    duration = end_time - start_time
    print "ID: " + idx + "," + " nr_of_comments: " + str(len(NER_count)) +  "," + " NER classification duration: " + str(int(duration)) + " seconds"



    NE_dict[idx] = output


  return NE_dict

def main():
  raw_data =  get_data()
  NER_categories = ["ORGANIZATION","PERSON","LOCATION","DATE","TIME","MONEY","PERCENT","FACILITY","GPE"]
  

  actions = []

  for article in raw_data:
      a = getArticleVector(article,NER_categories)
      output = []

      for ids, entities in a:
        b = []
        for entity, count in entities:
          a = {}
          a["name"] = entity[0]
          a["value"] = count
          a["label"] = entity[1]
          b.append(a)

        output.append((ids,b))
          
          
      #print output   

      articlestr = str(article['_id'])

      action = {
          "update":{
              "_index": 'controcurator',
              "_type": 'article',
              "_id": articlestr,

                      }

                }
      comments = []       

      for i,j in output:
          
          
          new_entity = {"entities": j
          }
                
          comments.append(new_entity)

        

      new_data = {
          "doc": {
              "comments":{ 
                
        }
        }
        }

      new_data['doc']['comments'] = comments

      #print new_data
      actions.append(action)
      actions.append(new_data)  

  print actions


if __name__ == "__main__":
  main()