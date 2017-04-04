import sys
reload(sys)
sys.setdefaultencoding('utf-8')

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
sys.path.insert(0, '..')
import os

import controllers.namedEntityExtractor as NE

###JAVA 1.8 required###
###Stanford-ner required###
###Change paths in models/summarization.py###
###Sample output in models/###


import elasticsearch
from elasticsearch import Elasticsearch, ConnectionTimeout,helpers


es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80,timeout=240)

nr_of_articles = 1


def get_data(corpus_size):
    query = {
      "query": {
        "bool": {
          "must": [
            {
              "constant_score": {
                "filter": {
                  "missing": {
                    "field": "article.source"
                  }
                }
              }
            }
          ]
        }
      },
      "from": 0,
      "size": nr_of_articles,
      "sort": [],
      "aggs": {}
    }

    response = es.search(index="controcurator", doc_type="article", body=query)
    data = response['hits']['hits']
    return data


def main():
  raw_data =  get_data(nr_of_articles)
  NER_categories = ["ORGANIZATION","PERSON","LOCATION","DATE","TIME","MONEY","PERCENT","FACILITY","GPE"]

  NE_list = NE.named_entities(raw_data,NER_categories)
  actions = []

  for article in NE_list.items():
      article_id = article[0]
      action = {
          "update":{
              "_index": 'controcurator',
              "_type": 'article',
              "_id": article_id,

                      }

                }
      comments = []       

      for items in article[1]:
          
          
          new_entity = {"entities": items
          }
                
          comments.append(new_entity)

        

      new_data = {
          "doc": {
              "comments":{ 
                
        }
        }
        }

      new_data['doc']['comments'] = comments

      
      actions.append(action)
      actions.append(new_data)  

  
  #print actions
  #es.bulk(index = "controcurator", body = actions)

if __name__ == "__main__":
  main()