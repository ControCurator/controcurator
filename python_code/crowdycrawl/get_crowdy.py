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

ARTICLES = 'http://q.crowdynews.com/v1/articles/controcurator'
SOCMEDS   = 'http://q.crowdynews.com/v1/collections/controcurator'

BASE = 'http://q.crowdynews.com'

client = elasticsearch.Elasticsearch()
INDEX  = 'crowdynews'
LOGDEX = 'crowdylog'

ARTCOUNT = 0
ARTCHILD = 0
SOCMED   = 0
SOCCHILD = 0
FAILURES = []

now = lambda: datetime.datetime.now().isoformat()
islist = lambda x: type(x)==list
isdict = lambda x: type(x)==dict

def get_articles(tries = MAXTRIES):
	articles = requests.get(ARTICLES).json()
	if isdict(articles) and articles.get('status','') and articles.get('status')=='error':
		print('retrying articles because {articles}'.format(**locals()))
		time.sleep(1)
		if tries > 0 : get_articles(tries-1)
		else:
			global FAILURES
			FAILURES.append('articles')
		return
	for article in articles:
		global ARTCOUNT
		ARTCOUNT += 1
		article['type']='article'
		article['retrieved'] =	now()
		client.index('crowdynews', doc_type=article['type'],body=article)
		get_article_children(article)

def get_article_children(article, tries = MAXTRIES):
	children = requests.get(BASE+article['url']).json()
	if isdict(children) and children.get('status','noerror')=='error':
		print('retrying article children because of {}'.format(children))
		time.sleep(1)
		if tries > 0 : get_article_children(article, tries=tries-1)
		else:
			global FAILURES
			FAILURES.append('article_children')
		return
	for child in children:
		global ARTCHILD
		ARTCHILD += 1
		child['parent'] = article
		child['retrieved'] = now()
		client.index(INDEX, id=child.get('id',None), doc_type=child.get('service','unknown'),body=child)

def get_socmed(tries = MAXTRIES):
	socmeds = requests.get(SOCMEDS).json()
	if isdict(socmeds) and socmeds.get('status','noerror')=='error': 
		time.sleep(1)
		print('retrying socmed retrieval because of {}'.format(socmeds))
		if tries > 0: get_socmed(tries=tries-1)
		else:
			global FAILURES
			FAILURES.append('socmed')
		return
	for socmed in socmeds:
		get_socchild(socmed)

def get_socchild(socmed, tries = MAXTRIES):
	global SOCMED
	SOCMED += 1
	children = requests.get(socmed['url']).json()
	if isdict(children) and children.get('status','noerror')=='error':
		print('retrying getting socchild because {}'.format(children))
		time.sleep(1)
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
		client.index(INDEX, id=child.get('id',None), doc_type=child.get('service','unknown'),body=child)

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
		article_children = ARTCHILD,
		socmed_queries = SOCMED,
		socmed_hits = SOCCHILD,
		errors = dict(Counter(FAILURES))
	)
	pprint(log)
	client.index(LOGDEX, doc_type='retrieval_log', body=log)
