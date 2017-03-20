'''
Import Guardian articles from JSON
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import json
import re
from urllib import quote

sys.path.insert(0,'../')
from models.article import Article
from controllers.sentimentExtractor import SentimentExtractor

from elasticsearch import Elasticsearch, ConnectionTimeout
from elasticsearch_dsl.connections import connections
import random

connections.create_connection(hosts=['http://controcurator.org:80/ess'])

es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)


directory = '/Users/benjamin/Downloads/controcurator_data_with_wiki_2/'
#directory = '/Users/benjamin/Downloads/source/'
#directory = '/Volumes/HDD/zips/source/'
Article.init()

files = os.listdir(directory)
totalfiles = len(files)
filenr = 0
for file in files:
  filenr += 1
  print filenr,'/',totalfiles,'files'
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

      comments = data['response']['content']['blocks']['comments']
      if comments is None:
        print 'no comments'
        continue
      comments = [c for c in comments if c['reply-to'] == ""]
      print len(comments),'comments'

      if len(comments) > 1000:
        print 'too many comments'
        continue



      try:
        existing = Article.get(id=id)
        if len(comments) == len(existing.comments):
          print 'existing article'
          continue
      except:
        print 'not yet in database'


      # try to find thumbnail
      #thumb = data['response']['content']['blocks']['body'][0]['elements']
      webtitle = data['response']['content']['webTitle'].encode('UTF-8').split(' | ')[0]
      section = data['response']['content']['sectionId']
      pubdate = data['response']['content']['webPublicationDate']

      html = data['response']['content']['blocks']['body'][0]['bodyHtml'].decode('ascii', 'ignore')
      paragraphs = html.split('</p>')
      stripHtml = lambda text: re.compile('(?!<p>|<br>|<br />)<.*?>').sub('',text)
      text = u'</p>'.join([stripHtml(p) for p in paragraphs])+'</p>'

      article = Article(meta={'id':id})
      article.url = url
      article.type = "article"
      article.source = "Guardian"
      article.published = pubdate
      article.document = {"title": webtitle, 'text': text}
      article.features = {"controversy" : {"random" : random.random()}}

      #print comments
      newcomments = []
      for comment in comments:
        if comment['reply-to'] == "":
          comment['sentiment'] = SentimentExtractor.getSentiment(comment['text'])
          newcomments.append(comment)
      article.comments = newcomments

      try:
        #print article
        article.save(index='controcurator')
        print 'success'
      except:
        print 'timeout'




