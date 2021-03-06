
import justext
import string
from pprint import pprint
from elasticsearch import Elasticsearch
from elasticsearch_dsl import DocType, Date, String, Nested
import re
import pandas as pd
from esengine import Document, ArrayField, StringField, ObjectField

es = Elasticsearch(['http://controcurator.org/ess/'], port=80)



# Articles are any kind of document

class getArticleMod(Document):
	_es = Elasticsearch(['http://controcurator.org/ess/'], port=80)
	_doctype = "article"
	_index = "controcurator"
	url = String(index='not_analyzed')

class markProcessed(Document):
	_es = Elasticsearch(['http://controcurator.org/ess/'], port=80)
	_doctype = "twitter"
	_index = "crowdynews"
	entities = ObjectField()
	processed = StringField()

class updateParent(Document):
	_es = Elasticsearch(['http://controcurator.org/ess/'], port=80)
	_doctype = "twitter"
	_index = "crowdynews"
	parent = ObjectField(properties={
		"url":String(index='not_analyzed')
	})

class Article(DocType):

	_es = Elasticsearch(['http://controcurator.org/ess/'], port=80)
	_type = "article"
	source = String(index='not_analyzed')
	type = String(index='not_analyzed')
	parent = String(index='not_analyzed')
	url = String(index='not_analyzed')
	published = Date()
	document = Nested(properties={
		"title":String(index='analyzed'),
		"image":String(index='not_analyzed'),
		"text":String(index='analyzed'),
		"author":String(index='analyzed')
		})
	comments = Nested(properties={
        'author-id': String(index='not_analyzed'),
        'author': String(index='not_analyzed'),
        'timestamp': Date(),
        'text' : String(),
        'reply-to': String(),
        'id': String()
    })

	class Meta:
		index = 'controcurator'









