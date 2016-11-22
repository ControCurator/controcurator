from elasticsearch import Elasticsearch
from esengine import Document, StringField, IntegerField, FloatField, DateField, ArrayField, ObjectField
from pprint import pprint
import time
import datetime

from pfe import *

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
	instances = ArrayField()
	count = IntegerField()
	positive = FloatField()
	negative = FloatField()
	controversy = FloatField()
	created = DateField()
	updated = DateField()

	@staticmethod
	def create(key, label):
		anchor = Anchor()

		# the current time
		now = lambda: datetime.datetime.utcnow().isoformat()
		anchor.id = key
		anchor.label = label
		anchor.instances = []
		anchor.count = 0
		anchor.positive = 0
		anchor.negative = 0
		anchor.controversy = 0
		anchor.created = now()
		anchor.updated = now()
		#anchor.save()
		#addInstance(instance)
		#updateCache()
		print 'NEW',key
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
			anchor = Anchor.create(key, label)
		return anchor

	def findInstances(self):
		# searches for new instances of this anchor
		key = self.id
		query = {"query":{"bool":{"must":[{"term":{"text":key}}]}},"size":1}
		response = es.search(index="crowdynews", body=query)
		for hit in response["hits"]["hits"]:
			self.addInstance(hit)
		update = self.updateCache()
		print update
		return update

	def updateCache(self):
		# update aggregated cache of features
		# returns count of previous existing entities, current entities and added entities
		update = {}
		update['previous'] = self.count
		update['current'] = len(self.instances)
		self.count = update['current']
		update['added'] = update['current'] - update['previous']
		return update

	def getInstances(self):
		# Return documents that this anchor appears in
		# TODO: change to actually getting the set of documents
		return self.instances


	def addInstance(self, instance):
		# adds this instance to the cache of the anchor
		if instance not in self.instances:
			if 'anchors' not in instance['_source']:
				# if the document is not analysed yet with the PFE, we must trigger this now
				getAnchors(instance)
			self.instances.append(instance['_id'])

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
		anchor = newAnchor('vaccination','autism','Autism','doc2')
		print_r(anchor)
		anchor = newAnchor('vaccination','needle','Needle','doc2')
		print_r(anchor)
		print anchor.firstInstance()
		break



		anchors = {}
		retrieved = now()
		# this should not occur, but just a safety check
		if 'retrieved' not in hit['_source']:
			continue
		date = hit['_source']['retrieved']
		if 'date' in hit['_source']:
			date = hit['_source']['date']

		for sentence in tagged:

			sentiment = getSentiment(sentence)
			#print sentiment
#			sentenceTopics = getTopics(sentence)
#			for t in sentenceTopics:
#				if t.lower() not in stop:
#					if t not in topics:
#						topics[t] = {'topic':t,'type':'NOUN','date':date,'retrieved':retrieved,'parent':hit['_id'],'service':hit['_type'],'count':0,'words':0,'positive':0,'negative':0,'intensity':0,'controversy':0}
#					topics[t]['count'] += 1
#					topics[t]['words'] += sentiment['count']
#					topics[t]['positive'] += sentiment['positive']
#					topics[t]['negative'] += sentiment['negative']
#					topics[t]['intensity'] = topics[t]['positive'] + (-1 * topics[t]['negative'])
#					topics[t]['controversy'] = topics[t]['intensity'] / max(abs(topics[t]['positive'] - (-1 * topics[t]['negative'])),1)
		
			for chunk in nltk.ne_chunk(sentence):
				if type(chunk) is nltk.Tree:
					t = ' '.join(c[0] for c in chunk.leaves())
					cat = chunk.label()
#					print t,cat
					if t not in topics:
						topics[t] = {'topic':t,'type':cat,'date':date,'retrieved':retrieved,'parent':hit['_id'],'service':hit['_type'],'count':0,'words':0,'positive':0,'negative':0,'intensity':0,'controversy':0}

					if t in topics:
						topics[t]['type'] = cat
					topics[t]['count'] += 1
					topics[t]['words'] += sentiment['count']
					topics[t]['positive'] += sentiment['positive']
					topics[t]['negative'] += sentiment['negative']
					topics[t]['intensity'] = topics[t]['positive'] + (-1 * topics[t]['negative'])
					topics[t]['controversy'] = topics[t]['intensity'] / max(abs(topics[t]['positive'] - (-1 * topics[t]['negative'])),1)


		if topics:
#			for t in topics:
				#print t+' - '+topics[t]['type']
			addBulk(topics)
		es.update(index = hit['_index'], doc_type=hit['_type'], id=hit['_id'], body = {'doc':{'tagged' : True}})
		#break
	#pprint(topics)