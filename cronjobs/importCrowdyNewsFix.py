'''
Due to an error some social media is missing the parent it is referring to.
This code reverts that issue.
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
import pandas as pd

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


connections.create_connection(hosts=['http://controcurator.org:80/ess'])

es = Elasticsearch(
		['http://controcurator.org/ess/'],
		port=80)




# get articles
# count socmed
query = {
  "query": {
"bool": {
"must": [
{
"match_all": { }
}
]
    }
  },
  "from": 0,
  "size": 10000
}




# count socmed
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
          "term": {
            "source": "vaccination"
          }
        },
        {
          "constant_score": {
            "filter": {
              "missing": {
                "field": "parent.url"
              }
            }
          }
        },
        {
          "constant_score": {
            "filter": {
              "missing": {
                "field": "source"
              }
            }
          }
        }
      ]
    }
  },
  "from": 0,
  "size": 10000
}


response = es.search(index="crowdynews", body=query)

data = response['hits']['hits']
actions = []
urls = {}

for socmed in data:

	url = unquote(re.sub('\/v1\/(.*[a-z])\/controcuratorguardian\?q=','',str(socmed['_source']['parent']['url']),))
	if url not in urls:
		urls[url] = {'socmed' : 0}
	urls[url]['socmed'] += 1


for url in urls:
	print url
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
		print "ARTICLE NOT FOUND"
		urls[url]['comments'] = 'nan'
	else:
		print "ARTICLE FOUND"
		if 'comments' not in response['hits']['hits'][0]['_source']:
			print "NO COMMENTS"
			continue
		urls[url]['comments'] = len(response['hits']['hits'][0]['_source']['comments'])


df = pd.DataFrame(urls).T
#freq = df
df.to_csv('socmed-urls.csv')


sys.exit('quit')









# build a list of all articles in the database
query = {
  "query": {
    "bool": {
      "must": {
        "match": {
          "_type": "article"
        }
      },
    "must_not": {
        "match": {
          "source": "vaccination"
        }
      }
    }
  },
  "from": 0,
  "size": 10000
}



{
  "query": {
    "bool": {
      "must_not": [
        {
          "term": {
            "source": "vaccination"
          }
        },
        {
          "constant_score": {
            "filter": {
              "missing": {
                "field": "parent.url"
              }
            }
          }
        },
        {
          "constant_score": {
            "filter": {
              "missing": {
                "field": "source"
              }
            }
          }
        }
      ]
    }
  },
  "from": 0,
  "size": 10
}


articles = es.search(index="crowdynews", body=query)
articles = articles['hits']['hits']

def getUrl(url):
	return unquote(re.sub('\/v1\/(.*[a-z])\/controcurator\?q=','',str(url),))


data = {getUrl(article['_source']['url']) : {'document' : article['_source']['url'],'title' : re.sub(u"(\u2018|\u2019)", "'", article['_source']['title'])} for article in articles}

print len(articles)
print len(data)

df = pd.DataFrame(data)
#freq = df
df.T.to_csv('article-freq.csv')

sys.exit('quit')






# build a list of all social media
# - which mention a url
# - do not have a parent yet
query = {
	"query": {
		"bool": {
			"must_not": [
				{
					"match": {
						"_type": "article"
					}
				},
				{
					"constant_score": {
						"filter": {
							"missing": {
								"field": "entities.urls"
							}
						}
					}
				}
			],
			"must": [
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
	"size": 1000
}
socmed = es.search(index="crowdynews", body=query)


for media in socmed['hits']['hits']:

	match = False
	id = media['_id']
	print id
	urls = media['_source']['entities']['urls']
	text = media['_source']['raw_text']

	# first check if one of the urls is a guardian url
	for url in urls:
		if 'guardian' in url['expanded_url']:
			match = url['expanded_url']
			continue
	
	# second check if title is in the text
	if not match:
		for article in articles:
			if article['_source']['title'] in text:
				match = article['_source']['url']

	if match:
		print id#, match
	else:
		print id,'not found'#, #text



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



