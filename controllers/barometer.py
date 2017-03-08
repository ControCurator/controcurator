#!/bin/python
import sys
import os


import random # while real data lacks
import json
# KB: Added modules
import numpy as np
import pandas as pd
import random

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q


es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)


if __name__=='__main__':

    '''
        Returns the top and bottom controversy articles
    '''

    if len(sys.argv) > 1:
        query = sys.argv[1]
        try:
            res = es.get(index="controcurator", doc_type="article", id=query)
            print(json.dumps(res['_source']))
        except:
            print(json.dumps({'status':'not_found'}))
        
    else:
        query = {
                "_source" : {
                "excludes" : ["comments"]
                },
              "query": {
                "match_all": {}
              },
              "sort": [
                {
                  "features.controversy.random": "desc"
                }
              ],
              "size" : 5
            }
        
        res = es.search(index="controcurator", doc_type="article", body=query)
        top = res['hits']['hits']

        query = {
                "_source" : {
                "excludes" : ["comments"]
                },
              "query": {
                "match_all": {}
              },
              "sort": [
                {
                  "features.controversy.random": "asc"
                }
              ],
              "size" : 5
            }
        
        res = es.search(index="controcurator", doc_type="article", body=query)
        bottom = res['hits']['hits']

        print(json.dumps({'top':top,'bottom':bottom}))

