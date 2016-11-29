from elasticsearch import Elasticsearch
from esengine import Document, StringField, IntegerField, FloatField, DateField, ArrayField, ObjectField
from pprint import pprint
import time
import datetime

from article import *

def print_r(the_object):
    print ("CLASS: ", the_object.__class__.__name__, " (BASE CLASS: ", the_object.__class__.__bases__,")")
    pprint(vars(the_object))

es = Elasticsearch(['http://controcurator.org/ess/'], port=80)


# A judgment is a person annotating a document
# Judgments can consist of multiple annotations, which indicate features of that document
# The annotations are aggregated into the document features
# Judgments should NEVER be edited or removed, instead the processing of the features may only change
class Judgment(Document):

	_es = Elasticsearch(['http://controcurator.org/ess/'], port=80)
	_index = "judgments"  # optional, it can be set after using "having" method
	_doctype = "annotation"  # optional, it can be set after using "having" method

	# initiate a new anchor
	# set existing anchor if it is in the database

	id = IntegerField() # A hash of the document+worker
	article = StringField()
	worker = StringField()
	content = ArrayField()
	accepted = DateField()
	submitted = DateField()


	@staticmethod
	def create(key, article, content, ip):
		judgment = Judgment()

		# the current time
		judgment.id = hash(article+ip)
		judgment.worker = ip
		judgment.content = content
		judgment.accepted = now()
		judgment.submitted = now()

		return judgment


	def getArticle(self):
		# return the entity of this judgment
		return Article().get(id=this.entity)

	def getArticleJudgments(self):
		# return a set with all judgments on this entity
		return []