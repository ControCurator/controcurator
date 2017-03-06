#!/bin/python
from __future__ import division
'''

This file provides an active learning environment for the demo interface.
Needs the file 'Topic.xlsx' as input.


Description of functionality
---

data model:
    COMMENT KASPAR: I interpreted 'score' as the class of the noun phrase, i.e. 0 or 1.
    datapoint = { str(noun phrase) : { 'score': float(controversy score), 'confidence':float(confidence)}}
    estimates = l st(datapoint1, .... , datapointN) 
    labelled  = { str(noun phrase) : { 'label' : 'controversial' OR 'noncontroversial') , 'ip' : str(ip address of user) } }

---

Controversy is labelled on the noun-phrase (here considered topic) level. 
Timestamps should be implemented on the backend side. 

'''
import random # while real data lacks
import json
import sys
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
from ..models import article


es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)


if __name__=='__main__':

    articles = article.Article.get(size=10)

    documents = loadDocuments()
    print(json.dumps(articles))

