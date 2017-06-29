import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import json
import re
import datetime
import pandas as pd

sys.path.insert(0,'../')
from elasticsearch import Elasticsearch, ConnectionTimeout
from models.article import Article
from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=['http://controcurator.org:80/ess'])

es = Elasticsearch(
	['http://controcurator.org/ess/'],
	port=80)

query = {
  "query": {
    "bool": {
      "must": [
        {
          "constant_score": {
            "filter": {
              "missing": {
                "field": "features.controversy.polarity"
              }
            }
          }
        }
      ],
      "must_not": [
        {
          "constant_score": {
            "filter": {
              "missing": {
                "field": "features.controversy.value"
              }
            }
          }
        }
      ]
    }
  },
  "from": 0,
  "size": 1000
}


res = es.search(index="controcurator", doc_type="article", body=query)
data = res['hits']['hits']

directory = '/'
results = {}
for hit in data:


	if 'comments' not in hit['_source']:
		print "SKIPPING"
		continue

	print hit['_id']

	features = hit['_source']['features']

	comments = hit['_source']['comments']

	if len([c for c in comments if 'sentiment' not in c]) > 0:
		continue

	features['controversy']['openness'] = len(comments)
	features['controversy']['actors'] = len(set(map(lambda x: x['author'], comments)))

	# get datetime of all comments
	times = list(map(lambda x: datetime.datetime.strptime(x['timestamp'][:-6], "%Y-%m-%dT%H:%M:%S"), comments))
	# add article post time to times
	times.append(datetime.datetime.strptime(hit['_source']['published'][:-6], "%Y-%m-%dT%H:%M:%S"))
	times = sorted(times)
	#r['times'] = times
	features['controversy']['duration'] = (times[-1] - times[0]).days + 1



	pos = list(filter(lambda x: x > 0, map(lambda x: x['sentiment']['sentiment'], comments)))
	neg = list(filter(lambda x: x < 0, map(lambda x: x['sentiment']['sentiment'], comments)))

	pos = sum(pos)
	neg = sum(map(abs, neg))
	
	intensity = list(map(lambda x: x['sentiment']['intensity'], comments))

	# compute polarity
	if neg <= 0 or pos <= 0:
		balance = 0
	else:
		balance = float(neg) / pos if pos > neg else float(pos) / neg

	features['controversy']['polarity'] = balance
	features['controversy']['emotion'] = sum(intensity) / len(intensity)

	Article.get(id=hit['_id']).update(features=features)

#df = pd.DataFrame(results).T
#df.to_csv('articlestats.csv')