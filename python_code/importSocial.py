'''
Uncomment the last line to enable updating of the database (read status
'''

from elasticsearch import Elasticsearch
from models.contro import SocialMedia, CrowdyMod
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=['http://controcurator.org:80/ess'])

es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)

query = {"query":
             {"bool":
                  { "must":
                        {"match":
                             {"service": "twitter|youtube|instagram" } #add more here
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

SocialMedia.init()

for resp in response['hits']['hits']:

    print resp['_type']

    continue
    newsocial = SocialMedia(meta={'id': resp['_id']})
    newsocial.url = resp['_source']['url']
    try:
        newsocial.document = {"text": resp['_source']['raw_text']}
    except KeyError:
        newsocial.document = {"text": resp['_source']['text']}
    try:
        newsocial.checkForParents(parenturl=resp['_source']['parent']['url'])
    except KeyError:
        newsocial.parent = ''

    newsocial.source = resp['_type']

    newsocial.features = {"kudos": resp['_source']['kudos'], "author": resp['_source']['author']}
    newsocial.save()
    # CrowdyMod.get(id=resp['_id']).update(Processed=1)



