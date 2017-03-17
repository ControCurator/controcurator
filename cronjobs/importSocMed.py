'''
Import Guardian articles from JSON
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import json
import re
from urllib import unquote
from elasticsearch import helpers

sys.path.insert(0,'../')
from models.article import Article
from controllers.sentimentExtractor import SentimentExtractor

from elasticsearch import Elasticsearch, ConnectionTimeout
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=['http://controcurator.org:80/ess'])
es = Elasticsearch(
	['http://controcurator.org/ess/'],
	port=80)



# first we make an index of all social media items and the parents they belong to
# then for each parent we get the social media items of that parent and put them as comment in the article


query = {
  "_source": {
    "includes": [
      "parent.url"
    ]
  },
  "query": {
	"bool": {
	  "must_not": [
		{
		  "constant_score": {
			"filter": {
			  "missing": {
				"field": "parent.url"
			  }
			}
		  }
		}
	  ]
	}
  },
  "from": 0,
  "size": 100
}


response = es.search(index="crowdynews", body=query)

data = response['hits']['hits']
actions = []

for socmed in data:

	url = unquote(re.sub('\/v1\/(.*[a-z])\/controcurator\?q=','',str(socmed['_source']['parent']['url']),))

	#print url
	query = {
	  "query": {
		"constant_score": {
		  "filter": {
			"term": {
			  "url": url
			}
		  }
		}
	  },
	  "from": 0,
	  "size": 1
	}


	response = es.search(index="controcurator", doc_type="article", body=query)
	if len(response['hits']['hits']) == 0:
		print "ARTICLE NOT FOUND, THIS SHOULD NOT HAPPEN"
		continue

	article = response['hits']['hits'][0]
	if 'comments' not in article['_source']:
		article['_source']['comments'] = []

	comment_ids = [comment['id'] for comment in article['_source']['comments']]
	if socmed['_source']['id'] in comment_ids:
		continue

	comment = {
	"author-id": socmed['_source']['author']['userid'],
	"author": socmed['_source']['author']['name'],
	"type" : socmed['_source']['service'],
	"timestamp": socmed['_source']['date'],
	"reply-to": "",
	"id": socmed['_source']['id'],
	}

	if 'raw_text' in socmed['_source']:
		comment["text"] = socmed['_source']['raw_text']
	else:
		comment["text"] = socmed['_source']['text']

		
	comment['sentiment'] = SentimentExtractor.getSentiment(comment['text'])
	article['_source']['comments'].append(comment)



	Article.get(id=article['_id']).update(comments=article['_source']['comments'])
	print 'updated',article['_id']







