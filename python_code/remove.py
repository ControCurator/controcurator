# removes a set of documents
from elasticsearch import Elasticsearch
from pprint import pprint
import time
import datetime

es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)
INDEX  = 'topics'
TYPES = 'vaccination'
LOGDEX = 'crowdylog'
now = lambda: datetime.datetime.utcnow().isoformat()



if __name__=='__main__':

	query = {
        "query" : {
            "bool" : { 
                "must" : {
                    "term" : { 
                        "tagged" : True
                    }
                }
            }
        },
		"size": 10000,
    }

	response= es.search(index="crowdynews", body=query)

	for hit in response["hits"]["hits"]:
		es.delete(index = hit['_index'], doc_type=hit['_type'], id=hit['_id'])
		#print('removed '+hit['_id'])