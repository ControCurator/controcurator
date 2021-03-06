'''
Import Articles from the crowdynews database
'''

import sys
import os

sys.path.insert(0,'../')


from elasticsearch import Elasticsearch
from models.article import Article, getArticleMod
from elasticsearch_dsl.connections import connections
from urllib import unquote
import random
from controllers.guardian_scraper import GuardianScraper
from string import replace
import re

import sys
reload(sys)
sys.setdefaultencoding('utf-8')



connections.create_connection(hosts=['http://controcurator.org:80/ess'])

es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)

query = {"query":
             {"bool":
                  { "must":
                        {"match":
                             {"_type":"article"}
                         }
                    }
              }
    ,"from": 0,"size":10000}
articles = es.search(index="crowdynews", body=query)


articles['hits']['hits']

print articles

sys.exit('quit')



getArticleMod.init()
Article.init()

gs = GuardianScraper()

for resp in response['hits']['hits']:

    cururl = unquote(re.sub('\/v1\/(.*[a-z])\/controcurator\?q=','',str(resp['_source']['url']),))

    if getArticleMod.count(url=cururl) > 0:
        print "Skipping: " + cururl
        continue
    print "Getting: " +cururl


    guardianresult = gs.retrieveArticle(cururl,True)[0]

    body = guardianresult['response']['content']['blocks']['body'][0]
    id = guardianresult['response']['content']['blocks']['body'][0]['id']
    url = guardianresult['response']['content']['webUrl']
    dtype = guardianresult['response']['content']['type']
    if dtype == 'article':
        # try to find thumbnail
        # thumb = data['response']['content']['blocks']['body'][0]['elements']
        webtitle = guardianresult['response']['content']['webTitle'].encode('UTF-8').split(' | ')[0]
        section = guardianresult['response']['content']['sectionId']
        pubdate = guardianresult['response']['content']['webPublicationDate']
        comments = guardianresult['response']['content']['blocks']['comments']
        try:
            print len(comments)
        except TypeError:
            comments = {}
        if len(comments) < 1000:
            html = guardianresult['response']['content']['blocks']['body'][0]['bodyHtml'].decode('ascii', 'ignore')
            paragraphs = html.split('</p>')
            stripHtml = lambda text: re.compile('(?!<p>|<br>|<br />)<.*?>').sub('', text)
            text = u'</p>'.join([stripHtml(p) for p in paragraphs]) + '</p>'

            article = Article(meta={'id': id})
            print id
            article.url = url
            article.type = "article"
            article.source = "crowdynews"
            article.published = pubdate
            article.document = {"title": webtitle, 'text': text}
            article.features = {"controversy": {"random": random.random()}}
            

            for comment in comments:
                print comment
                break
                #comments[comment]['sentiment'] = SentimentExtractor.getSentiment(comment['text'])



            article.comments = comments
            try:
                article.save(index='controcurator')
            except ConnectionTimeout:
                es = Elasticsearch(
                    ['http://controcurator.org/ess/'],
                    port=80)
                article.save(index='controcurator')



