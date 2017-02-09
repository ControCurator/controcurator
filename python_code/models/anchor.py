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


# An anchor is an entity for which we measure controversy
# This can be for instance a noun phrase, a named entity, a sentence
# Anchors are stored in the anchors index, whith their seed as document type (e.g. 'vaccination')
# Each instance of an anchor is cached in an anchor entity
class Anchor(Document):

	_es = Elasticsearch(['http://controcurator.org/ess/'], port=80)
	_index = "controcurator"  # optional, it can be set after using "having" method
	_doctype = "anchor"  # optional, it can be set after using "having" method

	# initiate a new anchor
	# set existing anchor if it is in the database

	id = StringField()
	label = StringField()
	instances = ObjectField()
	features = ObjectField()
	created = DateField()
	updated = DateField()

	@staticmethod
	def create(key):
		anchor = Anchor()

		# the current time
		now = lambda: datetime.datetime.utcnow().isoformat()
		anchor.id = key.replace(' ', '_').lower()
		anchor.label = key
		anchor.instances = {}
		anchor.features = {'instances' : 0, 'entities' : 0}
		anchor.created = now()
		anchor.updated = now()
		#anchor.save()
		#addInstance(instance)
		#updateCache()
		#print 'NEW',key
		return anchor

	@staticmethod
	def getOrCreate(key):

		# check if this anchor exists
		try:
			anchor = Anchor.get(id=key.replace(' ', '_').lower())
			#print 'EXISTING:',key
		#	print anchor
		except:
			# new anchor
			#print 'NEW',key.encode('utf-8')
			anchor = Anchor.create(key)
		return anchor

	def findInstances(self):
		# searches for new instances of this anchor
		key = self.id
		query = {"query":{"bool":{"must":[{"query_string":{"default_field":"_all","query":key}}]}},"size":2}
		response = es.search(index="controcurator", doc_type='article', body=query)
		#print 'FOUND',len(response["hits"]["hits"])
		for hit in response["hits"]["hits"]:
			self.addInstance(hit)
		self.updateCache()
		#print update
		return self.instances

	def updateCache(self):
		# update aggregated cache of features
		# returns count of previous existing entities, current entities and added entities
		features = self.features
		features['instances'] = len(self.instances)
		entities = {i+'-'+str(s):self.instances[i][s] for i in self.instances for s in self.instances[i]}
		features['entities'] = len(entities)
		#print 'Updated:',features['instances'] - self.features['instances']

		# update sentiment
		df = pd.DataFrame.from_dict(entities, orient='index')
		mean = df.mean()
		total = df.sum()
		features.update({k:v for k, v in mean.iteritems()})
		features.update({k:v for k, v in total.iteritems()})



		self.features = features

	def getInstances(self):
		# Return documents that this anchor appears in
		# TODO: change to actually getting the set of documents
		instances = Article.filter(ids=self.instances.keys())
		return instances._values


	def addInstance(self, instance):#, sentence, features):
		# adds this instance to the cache of the anchor
		if instance['_id'] not in self.instances:
			self.instances[instance['_id']] = {}

			
			if 'features' not in instance['_source']:
				# if the document is not analysed yet with the PFE, we must trigger this now
				article = Article.get(id=instance['_id'])
				#print_r(entity)
				features = article.getFeatures()
				#article.save()
			else:
				features = instance['_source']['features']
			
		self.instances[instance['_id']] = features
		self.updateCache()

	def setGroundTruth(self, feature, value):
		self.features['gt_'+feature] = value

