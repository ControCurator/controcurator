# removes a set of documents
from elasticsearch import Elasticsearch
from pprint import pprint
import time
import datetime

es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)
LOGDEX = 'crowdylog'
now = lambda: datetime.datetime.utcnow().isoformat()



if __name__=='__main__':

    query = {
        "query" : {
            "bool" : { 
                "must" : {
                    "term" : { 
                        "type" : 'article'
                    }
                }
            }
        },
        "size": 10000,
    }

    response= es.search(index="crowdynews", doc_type='article', body=query)

    for hit in response["hits"]["hits"]:
        print(hit['_index'],hit['_type'],hit['_id'])
        es.update(index = hit['_index'], doc_type=hit['_type'], id=hit['_id'], body={'doc': {'service':'article'}})