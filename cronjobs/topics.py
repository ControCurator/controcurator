'''
Import Guardian articles from JSON
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import json
import re

from elasticsearch import Elasticsearch, ConnectionTimeout
from models import Article

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
  "size": 10,
  "sort": [],
  "aggs": {}
}
response = es.search(index="controcurator", doc_type="article", body=query)

data = response['hits']['hits']



# topic classification
data

results


actions = []
for article in data:

    action = {
        "_index": "controcurator",
        "_type": "article",
        "_id": article['_id'],
        "_source": {
            "features": {
            "topics" : { 
              topics 

                }
            }
        }
    actions.append(action)

helpers.bulk(es, actions)





