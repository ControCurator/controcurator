import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import json
import re

from elasticsearch import Elasticsearch, ConnectionTimeout

es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)

query = {
      "query": {
        "match_all": {}
      },
      "size" : 10
    }

res = es.search(index="controcurator", doc_type="article", body=query)
data = res['hits']['hits']

directory = '/'

for hit in data:
	with open(directory+str(hit['_id'])+'.json', 'w') as outfile:
	    json.dump(hit, outfile, indent = 4)