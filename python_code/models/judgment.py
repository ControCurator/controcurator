from elasticsearch import Elasticsearch
from esengine import Document, StringField, IntegerField, FloatField, DateField, ArrayField, ObjectField
from pprint import pprint
import time
import datetime

from entity import *

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
	entity = StringField()
	worker = StringField()
	content = ArrayField()
	accepted = DateField()
	submitted = DateField()


	@staticmethod
	def create(key, entity, content, ip):
		judgment = Judgment()

		# the current time
		judgment.id = hash(entity+ip)
		judgment.worker = ip
		judgment.content = content
		judgment.accepted = now()
		judgment.submitted = now()

		return judgment


	def getDocument(self):
		# return the entity of this judgment
		return Entity().get(id=this.entity)

	def getDocumentJudgments(self):
		# return a set with all judgments on this entity
		return []