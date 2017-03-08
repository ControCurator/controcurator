'''
Import Guardian articles from JSON
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
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


directory = '/Users/benjamin/Downloads/controcurator_data_with_wiki_2/'

files = os.listdir(directory)
for file in files:
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
    dtype = data['response']['content']['type']
    if dtype == 'article':
      print id

      # try to find thumbnail
      #thumb = data['response']['content']['blocks']['body'][0]['elements']
      webtitle = data['response']['content']['webTitle'].encode('UTF-8').split(' | ')[0]
      section = data['response']['content']['sectionId']
      pubdate = data['response']['content']['webPublicationDate']
      comments = data['response']['content']['blocks']['comments']
      print len(comments)
      if len(comments) < 1000:
        html = data['response']['content']['blocks']['body'][0]['bodyHtml'].decode('ascii', 'ignore')
        paragraphs = html.split('</p>')
        stripHtml = lambda text: re.compile('(?!<p>|<br>|<br />)<.*?>').sub('',text)
        text = u'</p>'.join([stripHtml(p) for p in paragraphs[:2]])+'</p>'

        article = Article(meta={'id':id})
        article.url = url
        article.type = "article"
        article.source = "guardianJSON"
        article.published = pubdate
        article.document = {"title": webtitle, 'text': text}
        article.features = {"controversy" : {"score" : random.random()}}
        article.comments = comments
        article.save(index='controcurator',using=es)



