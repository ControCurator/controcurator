#!/bin/python

#import sys
import sys
sys.path.insert(0, '../models')
from article import Article

import random # while real data lacks
import json

import os
# KB: Added modules
import numpy as np
import pandas as pd
import random
# libact classes
from libact.base.dataset import Dataset
from libact.models import LogisticRegression
from libact.query_strategies import UncertaintySampling

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q


es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)


if __name__=='__main__':
    s = Search(using=es, index="controcurator")
    response = s.execute()
    print(json.dumps([hit for hit in response]))

