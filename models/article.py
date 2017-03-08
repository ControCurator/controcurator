
import justext
import string
from pprint import pprint
from elasticsearch import Elasticsearch
from elasticsearch_dsl import DocType, Date, Text, Nested, Keyword
import re
import pandas as pd

es = Elasticsearch(['http://controcurator.org/ess/'], port=80)



# Articles are any kind of document


class Article(DocType):

	_es = Elasticsearch(['http://controcurator.org/ess/'], port=80)
	_type = "document"
	source = Text(index='not_analyzed')
	type = Text(index='not_analyzed')
	parent = Text(index='not_analyzed')
	url = Text(index='not_analyzed')
	published = Date()
	document = Nested(properties={
		"title":Text(index='analyzed'),
		"image":Text(index='not_analyzed'),
		"text":Text(index='analyzed'),
		"author":Text(index='analyzed')
		})
	comments = Nested(properties={
        'author-id': Text(index='not_analyzed'),
        'author': Text(index='not_analyzed'),
        'timestamp': Date(),
        'text' : Text(),
        'reply-to': Text(),
        'id': Text()
    })
	features = Nested(properties={
		"quality":Nested(),
		"controversy":Nested(),
		"topics":Nested(),
		"author":Nested()
		})

	class Meta:
		index = 'controcurator'









