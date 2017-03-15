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

from elasticsearch import Elasticsearch, ConnectionTimeout,helpers
import controllers.topics_lda as Topics
import controllers.train_lda as Train
es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)



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
  "size": 10000,
  "sort": [],
  "aggs": {}
}
response = es.search(index="controcurator", doc_type="article", body=query)

data = response['hits']['hits']



'''
Topic Modeling LDA

'''
#train = Train.topic_train(data[0:4999])
#test = Topics.topic_load(data[4999:9999])
load_topics = Topics.topic_load(data)
result = collections.defaultdict(list,load_topics)

actions = []
for article in data:
    output = {}
    topics = result[article['_id']]

    for i,j in topics:
        topic_score = i +" " + "("+str(j)+")"
        output[i] = j


    action = {
        "_op_type": "update",
        "_index": "controcurator",
        "_type": "article",
        "_id": str(article['_id']),
        "_source": {
            "features": {
                "topics" : { 

                    }
            }
        }
    }
    action["_source"]["features"]["topics"] = output
    actions.append(action)

helpers.bulk(es, actions)





