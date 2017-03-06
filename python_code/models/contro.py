
import justext
import string
from pprint import pprint
from elasticsearch import Elasticsearch
from elasticsearch_dsl import DocType, Date, String, Nested
import re
import pandas as pd


from anchor import *


es = Elasticsearch(['http://controcurator.org/ess/'], port=80)



# Articles are any kind of document


class Article(DocType):

	_es = Elasticsearch(['http://controcurator.org/ess/'], port=80)
	_type = "document"
	source = String(index='not_analyzed')
	type = String(index='not_analyzed')
	parent = String(index='not_analyzed')
	url = String(index='not_analyzed')
	published = Date()
	document = Nested(properties={"title":String(index='analyzed'),"image":String(index='not_analyzed'),"text":String(index='analyzed'),"author":String(index='analyzed')})
	#features = Nested(properties={"quality":Nested(),"controversy":Nested()})

	class Meta:
		index = 'controcurator'




class SocialMedia(DocType):
	_es = Elasticsearch(['http://controcurator.org/ess/'], port=80)
	_type = "socialmedia"

	source = String(index='not_analyzed')
	#type = String(index='not_analyzed')
	parent = String(index='not_analyzed')
	url = String(index='not_analyzed')
	published = Date()
	document = Nested(properties={"title":String(index='analyzed'),"image":String(index='not_analyzed'),"text":String(index='analyzed'),"author":String(index='analyzed')})
	features = Nested(properties={"kudos":Nested(),"author":Nested()})


	class Meta:
		index = 'controcurator'

	def checkForParents(self, parenturl):
		if parenturl == '':
			return
		print parenturl

		findparentquery = {"query":
							   {"bool":
									{"must":
										  {"match":
											   {"url":parenturl }
										   }
									  }
								}
						   }
		response = es.search(index="controcurator", body=findparentquery)

		if len(response['hits']['hits']) > 0:
			self.parent = response['hits']['hits'][0]['_id'];


class CrowdyMod(Document):
    _es = Elasticsearch(['http://controcurator.org/ess/'], port=80)
    _index = "joran"
    _doctype = "article"

    Processed = IntegerField()








