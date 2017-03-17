import sys
sys.path.insert(0,'../')

from elasticsearch import Elasticsearch
from models.article import updateParent
from urllib import unquote, quote
import pprint
import sys
import re
from esengine import Payload
reload(sys)
sys.setdefaultencoding('utf-8')


class BreakOutOfLoop(Exception): pass

es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)

query = {"query":
             {"bool":
                  { "must":
                        {"match":
                             {"_type":"twitter"}
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
    ,"from": 0}

#markProcessed.init()

curdict = {}
t = es.search(index='crowdynews',doc_type='twitter',body = query,scroll='2m',size=1000)
scroll_id = t['_scroll_id']
scroll_size = t['hits']['total']

urlprefix = '/v1/related/controcurator?q='

hitcounter = 0
nothitcounter = 0
notguardiancounter = 0
noturlscounter = 0
while scroll_size > 0:
    for curt in t['hits']['hits']:

        curlist = []
        try:
            for urle in curt['_source']['entities']['urls']:
                if str(urle['expanded_url']).find('guardian') < 0:
                    notguardiancounter += 1
                    raise BreakOutOfLoop
                curlist.append(urle['expanded_url'])
        except KeyError:
            noturlscounter += 1
            continue
        except BreakOutOfLoop:
            continue

        try:
            curparent = curt['_source']['parent']['url']
            curparent = unquote(re.sub('\/v1\/(.*[a-z])\/controcurator\?q=', '', curparent))
        except KeyError:
            curparent = ''

        if len(curlist) > 0:
            curdict[curt['_id']] = curlist

        if curparent in curlist:
            hitcounter += 1
        else:
            nothitcounter += 1
            getdoc = updateParent.get(id=curt['_id'])
            buildurl = urlprefix + quote(curlist[0],safe='')
            getdoc.update(parent={'url':buildurl})

    t = es.scroll(scroll_id=scroll_id,scroll='2m')
    scroll_size = len(t['hits']['hits'])
    print "Hits: " + str(hitcounter) + " -- Not hits (updated): " + str(nothitcounter) + " -- Not guardian: "+str(notguardiancounter)+" -- No urls: "+str(noturlscounter)
#print "Hits: "+str(hitcounter)+" -- Not hits: "+str(nothitcounter)
