import sys
import json
import pprint
from elasticsearch import Elasticsearch
from esengine import ObjectField, Document
import pandas as pd


class updateModel(Document):
    features = ObjectField(properties={"controversy":ObjectField(properties={'kasparfier':ObjectField(type='double')})})
    _es = Elasticsearch(['http://controcurator.org/ess/'], port=80)
    _index = "controcurator"
    _doctype = "article"


es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)


importresults = open('/Users/benjamin/Downloads/controcurator/results.csv')

crowdlabels = pd.read_csv(importresults)

notfoundcount = 0
foundcount = 0
skipped = 0
actions = []

for index, row in crowdlabels.iterrows():

    id = row['input.id']
    workers = row['worker']
    controversy = row['output.controversy'][8:-1]
    controversy = controversy.replace("'","\"")
    controversy = json.loads(controversy)

    print id
    try:
        res = es.get(index='controcurator',doc_type='article',id=id)
        if 'value' in res['_source']['features']['controversy']:
            print 'skipping because classified'
            skipped += 1
            continue
        vector = {
            'polarity' : controversy['polarity_yes'] / float(workers),
            'popularity' : controversy['popularity_yes'] / float(workers),
            'openness' : controversy['openness_yes'] / float(workers),
            'sentiment' : controversy['sentiment_yes'] / float(workers),
            'persistence' : controversy['persistence_yes'] / float(workers),
            'controversy' : controversy['controversial_yes'] / float(workers),
        }
        combined = (vector['polarity'] + vector['popularity'] + vector['openness'] + vector['sentiment'] + vector['persistence']) / float(workers)
        vector['value'] = (vector['controversy'] + combined) / 2

        foundcount += 1

        es.update(index='controcurator',doc_type='article',id=id,
            body={"doc": {"features": {"controversy":vector}}})
        print 'saved'
    except:
        notfoundcount += 1

print "Found: "+str(foundcount)+ " -- NOT found: "+str(notfoundcount)+ " -- Skipped: "+str(skipped)




