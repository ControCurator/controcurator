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


# An anchor is an entity for which we measure controversy
# This can be for instance a noun phrase, a named entity, a sentence
# Anchors are stored in the anchors index, whith their seed as document type (e.g. 'vaccination')
# Each instance of an anchor is cached in an anchor entity
class Anchor(Document):

	_es = Elasticsearch(['http://controcurator.org/ess/'], port=80)
	_index = "anchors"  # optional, it can be set after using "having" method
	_doctype = "vaccination"  # optional, it can be set after using "having" method

	# initiate a new anchor
	# set existing anchor if it is in the database

	id = StringField()
	label = StringField()
	instances = ObjectField()
	features = ObjectField()
	created = DateField()
	updated = DateField()

	@staticmethod
	def create(key, label):
		anchor = Anchor()

		# the current time
		now = lambda: datetime.datetime.utcnow().isoformat()
		anchor.id = key
		anchor.label = label
		anchor.instances = {}
		anchor.features = {'total_instances' : 0}
		anchor.created = now()
		anchor.updated = now()
		#anchor.save()
		#addInstance(instance)
		#updateCache()
		#print 'NEW',key
		return anchor

	@staticmethod
	def getOrCreate(seed, key, label):

		# check if this anchor exists
		try:
			anchor = Anchor.get(id=key)
			print 'EXISTING:',key
		#	print anchor
		except:
			# new anchor
			print 'NEW',key
			anchor = Anchor.create(key, label)
		return anchor

	def findInstances(self):
		# searches for new instances of this anchor
		key = self.id
		query = {"query":{"bool":{"must":[{"query_string":{"default_field":"_all","query":key}},{"term":{"service":"webpage"}}]}},"size":2}
		response = es.search(index="crowdynews", body=query)
		print 'FOUND',len(response["hits"]["hits"])
		for hit in response["hits"]["hits"]:
			self.addInstance(hit)
		self.updateCache()
		#print update
		return self.instances

	def updateCache(self):
		# update aggregated cache of features
		# returns count of previous existing entities, current entities and added entities
		features = {}
		features['total_instances'] = len(self.instances)
		print 'Updated:',features['total_instances'] - self.features['total_instances']

		# update sentiment
		df = pd.DataFrame.from_dict(self.instances, orient='index')
		mean = df.mean()
		total = df.sum()
		features.update({k:v for k, v in mean.iteritems()})
		features.update({k:v for k, v in total.iteritems()})



		self.features = features

	def getInstances(self):
		# Return documents that this anchor appears in
		# TODO: change to actually getting the set of documents
		return self.instances


	def addInstance(self, instance):
		# adds this instance to the cache of the anchor
		if instance['_id'] not in self.instances:
			if 'features' not in instance['_source']:
				# if the document is not analysed yet with the PFE, we must trigger this now
				entity = Entity.get(id=instance['_id'])
				#print_r(entity)
				features = entity.getFeatures()
				#entity.save()
			self.instances[instance['_id']] = features

	def firstInstance(self):
		return 'first'

	def lastInstance(self):
		return 'last'






def addBulk(anchors):
	bulk_data = [] 
	for child in anchors:
		data_dict = {}
		for i in anchors[child]:
			data_dict[i] = anchors[child][i]

		op_dict = {
			"create": {
				"_index": INDEX, 
				"_type": TYPES, 
				"_id": hash(anchors[child]['topic']+anchors[child]['parent'])
			}
		}
		bulk_data.append(op_dict)
		bulk_data.append(data_dict)

	#pprint(bulk_data)
	res = es.bulk(index = INDEX, body = bulk_data)

if __name__=='__main__':

	Anchor.init()

	query = {
	    "query" : {
	        "bool" : { 
	            "must_not" : {
	                "term" : { 
	                    "tagged" : True
	                }
	            }
	        }
	    },
		"size": 10,
	}

	response= es.search(index="crowdynews", body=query)

	for hit in response["hits"]["hits"]:

		anchor = newAnchor('vaccination','needle','Needle','doc1')
		print_r(anchor)
#		anchor = newAnchor('vaccination','autism','Autism','doc2')
#		print_r(anchor)
#		anchor = newAnchor('vaccination','needle','Needle','doc2')
#		print_r(anchor)
		print anchor.firstInstance()
		break
	


		if topics:
#			for t in topics:
				#print t+' - '+topics[t]['type']
			addBulk(topics)
		es.update(index = hit['_index'], doc_type=hit['_type'], id=hit['_id'], body = {'doc':{'tagged' : True}})
		#break
	#pprint(topics)