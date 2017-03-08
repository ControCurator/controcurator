import sys
import json
import pprint
from elasticsearch import Elasticsearch
from esengine import ObjectField, Document


class updateModel(Document):
    features = ObjectField(properties={"controversy":ObjectField(properties={'kasparfier':ObjectField(type='double')})})
    _es = Elasticsearch(['http://controcurator.org/ess/'], port=80)
    _index = "controcurator"
    _doctype = "article"


es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)


importjson = open('/Volumes/HDD/zips/id_proba_mapping.json')

actualjson = json.load(importjson)

notfoundcount = 0;
foundcount = 0;

for index in actualjson:

    insertscore = actualjson[index][0]


    query = {
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "_id": index
                    }
                }
            }
        },
        "from": 0,
        "size": 1
    }

    res = es.search(index='controcurator',doc_type='article',body=query)

    if len(res['hits']['hits']) < 1:
        notfoundcount += 1
    else:
        foundcount += 1
        updateModel.get(id=index).update(features={'controversy':{'kasparfier':insertscore}})


print "Found: "+str(foundcount)+ " -- NOT found: "+str(notfoundcount)






