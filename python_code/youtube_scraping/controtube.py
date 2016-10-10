#!/bin/python
'''
crawls the youtube search results for terms specified in terms.txt (one per line). 

usage:

controtube.py [starterm] [searchpage] 

starterm   = the term to resume search
searchpage = the last unfinished search page 

Requires a running elasticsearch instance on port 9200!

'''

from youtube import *
import json
import elasticsearch
import datetime
import sys

CONTROTUBE_INDEX = 'controtube'
CONTROTUBE_LOGS  = 'controlog'


client = elasticsearch.Elasticsearch()
now = lambda: datetime.datetime.now().isoformat()

terms = [term.strip() for term in open('terms.txt').readlines() if term.strip()]

def resume(startterm=None, searchpage=None):
	for nterm, term in enumerate(terms):
		if startterm and term!= startterm: continue
		startterm = None # after resuming at the specified term, we can forget the startpoint
		for nvideo, video in enumerate(search(term, expand=True, nextPageToken=searchpage)):
			searchpage = None # at this point the start page is no longer current
			video['TERM_MATCH'] = term
			video['caption_en'] = get_caption(video, language='en')
			client.index(CONTROTUBE_INDEX, doc_type='video', id=video['id'], body=video)
			for ncomment, comment in enumerate(get_comments(video)):
				client.index(CONTROTUBE_INDEX, doc_type='comment', id=comment['id'], body=comment)
				n = now()
				print("{n} at term {nterm} ({term}) - video {nvideo} - comment {ncomment}".format(**locals()))
		log = dict(at=now(),term=term,nterm=nterm, page=video.get('PAGE',''), ncomments=comment)
		client.index(CONTROTUBE_LOGS,doc_type='log', body=log)

def last_state():
	last = client.search(CONTROTUBE_LOGS, body={'sort':{'at':'desc'}}).get('hits',{}).get('hits',[])
	if len(last)>0:
		startterm = last['_source']['term']
		searchpage = last['_source']['page']
		print('resumable at {startterm}, {searchpage}'.format(**locals()))
	else:
		startterm=None
		searchpage=None
	return starterm, searchpage

if __name__=='__main__':
	if len(sys.argv)>2:
		starterm = sys.argv[1]
		if startterm=='resume':
			resume(*last_state())
			print('done')
			exit()
	else:
		starterm = None
	if len(sys.argv)>3:
		searchpage = sys.argv[2]
	else:
		searchpage = None
	resume(starterm, searchpage)
	
			
			
