
import justext
import string
from pprint import pprint
from elasticsearch import Elasticsearch
from elasticsearch_dsl import DocType, Date, String, Nested
import re
import pandas as pd

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









