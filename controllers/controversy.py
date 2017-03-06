#!/bin/python
import random # while real data lacks
import json

import sys
import os
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
        Given a set of documents, this return the controversy scores
    '''

    if len(sys.argv) > 1:
        query = sys.argv[1]
        try:
            res = es.get(index="controcurator", doc_type="article", id=query)
            print(json.dumps(res['_source']))
        except:
            print(json.dumps({'status':'not_found'}))
        
    else:
        res = es.search(index="controcurator", doc_type="article", body={"query": {"match_all": {}}})
        print(json.dumps(res['hits']['hits']))

