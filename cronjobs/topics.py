'''
Import Guardian articles from JSON
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import json
import re
import collections

sys.path.insert(0, '..')
import elasticsearch
from elasticsearch import Elasticsearch, ConnectionTimeout,helpers
import controllers.topics_lda as Topics
import controllers.train_lda as Train
es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80,timeout=60)



query = {
  "_source": {
    "excludes": [
      "comments"
    ]
  },
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
  "size": 5000,
  "sort": [],
  "aggs": {}
}
response = es.search(index="controcurator", doc_type="article", body=query)

data = response['hits']['hits']




'''
TOPIC MODELING LDA
'''
'''
Train MODEL
'''
#train = Train.topic_train(data)

'''
Classify articles

'''
load_topics = Topics.topic_load(data)
result = collections.defaultdict(list,load_topics)

actions = []
for article in data:
    topics = result[article['_id']]
    output = []
    names = []
    values = []

    for i,j in topics:
        #topic_score = i +" " + "("+str(j)+")"
        a = {}
        a["name"] = i
        a["value"] = j
        
        output.append(a)
    

    articlestr = str(article['_id'])

    action = {
        "update":{
            "_index": 'controcurator',
            "_type": 'article',
            "_id": articlestr
            
      }
    }


    new_data = {
        "doc": {
            "features":{ 
          }
        }
    }
    new_data['doc']['features']['topics'] = output

    
    actions.append(action)
    actions.append(new_data)



#es.bulk(index = "controcurator", body = actions)





