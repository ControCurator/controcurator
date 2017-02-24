# import guardian articles
import os
import json
from models.articles.crowdynews import *
from elasticsearch import Elasticsearch


es = Elasticsearch(
	['http://controcurator.org/ess/'],
	port=80)

# main function
if __name__=='__main__':

	#articles = CrowdyNews.all(size=1000)
	#CrowdyNews.delete_all(articles)

	anchors = Anchor.all(size=1000)
	#Anchor.delete_all(anchors)

	query = {"query" : {"match_all" : {}}, "from": 0, "size": 1000}

	# load cached entries
	response = es.search(index="crowdynews", body=query)

	for f in response["hits"]["hits"]:

		# for each file
		data = f['_source']
		article = CrowdyNews.create(data)
		article.save()
		# add article


			# add comments as article children


		# add wiki topics as anchors
		
		for anchor in anchors:
			a = Anchor.getOrCreate(anchor.id.lower())
			a.findInstances()
			a.save()
		
		
		#print added article.id