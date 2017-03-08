'''
Currently, updating received articles is disabled!
'''

import sys
import os

sys.path.insert(0,'../')
from models import article

from elasticsearch import Elasticsearch
from models import Article
from elasticsearch_dsl.connections import connections
import random

connections.create_connection(hosts=['http://controcurator.org:80/ess'])

es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)

query = {"query":
             {"bool":
                  { "must":
                        {"match":
                             {"_type":"article"}
                         }
                      , "must_not":
                        {
                            "match":
                                {
                                    "Processed" : "1"
                                }
                        }
                    }
              }
    ,"from": 0,"size":10000}
response = es.search(index="crowdynews", body=query)

#Article.init()

for resp in response['hits']['hits']:

    print resp['_id']
    newarticle = Article(meta={'id':resp['_id']})
    newarticle.url = resp['_source']['url']
    newarticle.type = "article"
    newarticle.published = resp['_source']['retrieved']
    newarticle.document = {"title": resp['_source']['title']}
    newarticle.features = {"controversy" : random.random()}
    newarticle.save(index='controcurator',using=es)
    print newarticle.features.controversy
    #CrowdyMod.get(id=resp['_id']).update(Processed=1)



