'''
Import Guardian articles from JSON
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import json
import re
from urllib import unquote
from elasticsearch import helpers
import pandas as pd

sys.path.insert(0,'../')
from models.article import Article
from controllers.sentimentExtractor import SentimentExtractor

from elasticsearch import Elasticsearch, ConnectionTimeout
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=['http://controcurator.org:80/ess'])
es = Elasticsearch(
  ['http://controcurator.org/ess/'],
  port=80)



# first we make an index of all social media items and the parents they belong to
# then for each parent we get the social media items of that parent and put them as comment in the article


query = {
  "_source": {
    "includes": [
      "parent.url",
      "retrieved",
      "date"
    ]
  },
  "query": {
    "bool": {
      "must_not": [
        {
          "constant_score": {
            "filter": {
              "missing": {
                "field": "parent.url"
              }
            }
          }
        }
      ]
    }
  },
  "from": 0
}

response = es.search(index="crowdynews", body=query,scroll='2m',size=1000)
scroll_id = response['_scroll_id']
scroll_size = response['hits']['total']
urls = []

while scroll_size > 0:
  print 'remaining:',scroll_size
  data = response['hits']['hits']

  for socmed in data:

    url = unquote(re.sub('\/v1\/(.*[a-z])\/controcurator\?q=','',str(socmed['_source']['parent']['url']),))
    try:
      date = socmed['_source']['retrieved']
    except:
      try:
        date = socmed['_source']['date']
      except:
        print 'failed',socmed['_id']
        continue
    urls.append([url,date])
    
  response = es.scroll(scroll_id=scroll_id,scroll='2m')
  scroll_size = len(response['hits']['hits'])

df = pd.DataFrame(urls)
freq = df[0].value_counts()
#freq = df
freq.to_csv('socmed-freq.csv')
#print urls








