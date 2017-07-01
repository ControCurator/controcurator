#!/bin/python
__author__ = 'Kaspar Beelen (k.beelen@uva.nl) and Benjamin Timmermans (b.timmermans@vu.nl)'
import sys
import os

import requests
import re
import json
from sklearn.externals import joblib
from sklearn.pipeline import Pipeline

if __name__=='__main__':


    stripHTML = lambda x: re.compile('<.*?>').sub('',x)

    path = os.path.dirname(os.path.realpath(__file__))

    pipeline = joblib.load(path+'/controcurator_model_2.pkl')


    '''
        Given a set of documents, this return the controversy scores
    '''

    query = sys.stdin.readlines()[0]
    query = json.loads(query)
    texts = [stripHTML(e.get('text',' ')) for e in query]
    texts = ['\n'.join(texts)]

    controversy = float(pipeline.predict(texts)[0])
    confidence = float(pipeline.decision_function(texts))
    #print controversy
    print({'controversy':controversy, 'confidence':confidence})


