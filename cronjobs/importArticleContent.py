'''
Currently, updating received articles is disabled!
'''

import sys
import os
import json
import re

sys.path.insert(0,'../')
from models import article
from urllib import quote

from elasticsearch import Elasticsearch
from models import Article
from elasticsearch_dsl.connections import connections
import random


connections.create_connection(hosts=['http://controcurator.org:80/ess'])

es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)


directory = '/Users/benjamin/Downloads/source/'

files = os.listdir(directory)
for file in files[0:100]:
  # for each file in the directory
  # find the matching guardian article in the database
  # add the content of the file to the article in the database

  if file.startswith('.'):
    continue
  with open(directory+file) as f:

    data = json.load(f)
    body = data['response']['content']['blocks']['body'][0]
    id = data['response']['content']['blocks']['body'][0]['id']
    url = data['response']['content']['webUrl']
    print url
    urlquote = "/v1/related/controcurator?q="+quote(url, safe='')
    print urlquote

    query = {
      "query": {
        "constant_score": {
          "filter": {
            "term": {
              "url": urlquote
            }
          }
        }
      },
      "from": 0,
      "size": 1
    }

    response = es.search(index="controcurator", doc_type="article", body=query)
    resp = response['hits']['hits']
    if len(resp) == 0:
      print "NOT FOUND"
    else:
      print resp

      webtitle = data['response']['content']['webTitle'].encode('UTF-8').split(' | ')[0]
      dtype = data['response']['content']['type']
      section = data['response']['content']['sectionId']
      pubdate = data['response']['content']['webPublicationDate']

      html = data['response']['content']['blocks']['body'][0]['bodyHtml']
      paragraphs = html.split('</p>')
      paragraphCount = len(paragraphs)
      stripHtml = lambda text: re.compile('(?!<p>|<br>|<br />)<.*?>').sub('',text)
      text = '</p>'.join([stripHtml(p) for p in paragraphs[:2]])+'</p>'

      '''
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
      '''



