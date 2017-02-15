#!/bin/python
'''
 Get Crowdynews articles for the controcurator project
'''
import elasticsearch
import requests
import datetime
import time
from collections import Counter
from pprint import pprint

MAXTRIES = 5

ARTICLES = 'http://q.crowdynews.com/v1/articles/controcurator?count=100'
SOURCE = 'guardian-vaccination'
SOCMEDS = 'https://q.crowdynews.com/v1/content/controcurator?q=BOxE9ZZ-vaccination&count=100'

BASE = 'http://q.crowdynews.com'

client = elasticsearch.Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)
INDEX  = 'crowdynews'
LOGDEX = 'crowdylog'

ARTCOUNT = 0
ARTCOUNTNEW = 0
ARTCHILD = 0
ARTCHILDNEW = 0
SOCMED   = 0
SOCCHILD = 0
FAILURES = []

now = lambda: datetime.datetime.utcnow().isoformat()
islist = lambda x: type(x)==list
isdict = lambda x: type(x)==dict

def get_articles(tries = MAXTRIES):
	articles = requests.get(ARTICLES).json()
	if isdict(articles) and articles.get('status','') and articles.get('status')=='error':
		print('retrying articles because {articles}'.format(**locals()))
		#time.sleep(1)
		if tries > 0 : get_articles(tries-1)
		else:
			global FAILURES
			FAILURES.append('articles')
		return
	for article in articles:
		global ARTCOUNT
		ARTCOUNT += 1
		article['service'] = 'article'
		article_id = hash(article['url'])
		article['retrieved'] =	now()
		article['source'] =	SOURCE
		res = client.index('crowdynews', id=article_id, doc_type=article['service'],body=article)
		if(res['created'] == True):
			global ARTCOUNTNEW
			ARTCOUNTNEW += 1
			print('Added '+article['service']+' '+res['_id'])
		else:
			print('Existing '+article['service']+' '+res['_id'])
		print res['_id']
		#pprint(article)
		get_article_children(article, article_id)

def get_article_children(article, article_id, tries = MAXTRIES):
	children = requests.get(BASE+article['url']).json()
	if (len(children) == 0):
		return
	if (isdict(children) and children.get('status','noerror')=='error'):
		#print('retrying article children because of {}'.format(children))
		#time.sleep(1)
		#if tries > 0 : get_article_children(article, tries=tries-1)
		#else:
		global FAILURES
		FAILURES.append('article_children')
		return


	bulk_data = [] 
	artChildren = 0
	time = now()
	for child in children:
	    data_dict = {}
	    for i in child:
			artChildren += 1
			data_dict[i] = child[i]
	    data_dict['parent'] = article_id
	    data_dict['retrieved'] = time
	    data_dict['source'] = SOURCE
	    pprint(data_dict)
	    op_dict = {
	        "create": {
	            "_index": INDEX, 
	            "_type": child.get('service','unknown'), 
	            "_id": data_dict['id']
	        }
	    }
	    bulk_data.append(op_dict)
	    bulk_data.append(data_dict)


	res = client.bulk(index = INDEX, body = bulk_data)
	#pprint(res)
	# see how many succeeded

	artChildrenNew = 0
	for r in res['items']:
		#print r['create']['error']
		if(r['create']['status'] != 409):
			artChildrenNew += 1
			#print('Added new child '+r['create']['_type'])

	global ARTCHILD
	ARTCHILD += artChildren
	global ARTCHILDNEW
	ARTCHILDNEW += artChildrenNew
	#print('Ignored children: '+str(artChildren-artChildrenNew))



def get_socmed(tries = MAXTRIES):
	socmeds = requests.get(SOCMEDS).json()
	if isdict(socmeds) and socmeds.get('status','noerror')=='error': 
		#time.sleep(1)
		print('retrying socmed retrieval because of {}'.format(socmeds))
		if tries > 0: get_socmed(tries=tries-1)
		else:
			global FAILURES
			FAILURES.append('socmed')
		return
	for socmed in socmeds:
		global SOCCHILD
		SOCCHILD +=1
		socmed['retrieved'] = now()
		socmed['source'] = SOURCE
		res = client.index(INDEX, id=socmed.get('id',None), doc_type=socmed.get('service','unknown'),body=socmed)
		print('retrieved '+socmed.get('service','unknown')+' status: '+str(res['created'])+' id: '+socmed.get('id',None))
		#get_socchild(socmed)

def get_socchild(socmed, tries = MAXTRIES):
	global SOCMED
	SOCMED += 1
	if socmed['url'] == None:
		print('socchild had no url')
		return

	children = requests.get(socmed['url']).json()
	if isdict(children) and children.get('status','noerror')=='error':
		print('retrying getting socchild because {}'.format(children))
		#time.sleep(1)
		if tries > 0 : get_socchild(socmed)
		else:
			global FAILURES
			FAILURES.append('socmed_hits')
		return
	for child in children:
		global SOCCHILD
		SOCCHILD +=1
		child['parent'] = socmed
		child['retrieved'] = now()
		child['source'] = SOURCE
		res = client.index(INDEX, id=child.get('id',None), doc_type=child.get('service','unknown'),body=child)
		print('retrieved '+child.get('service','unknown')+' status: '+str(res['created'])+' id: '+child.get('id',None))

if __name__=='__main__':
	start = now()
	print('started at {}'.format(start))
	print('retieving articles at {}'.format(now()))
	get_articles()
	print('retrieving social media at {}'.format(now()))
	get_socmed()
	print('finished at {}'.format(now()))
	log = dict(
		starttime = start,
		enddtime  = now(),
		articles  = ARTCOUNT,
		articles_new = ARTCOUNTNEW,
		article_children = ARTCHILD,
		article_children_new = ARTCHILDNEW,
		socmed_queries = SOCMED,
		socmed_hits = SOCCHILD,
		errors = dict(Counter(FAILURES))
	)
	pprint(log)
	client.create(LOGDEX, doc_type='retrieval_log', body=log)

