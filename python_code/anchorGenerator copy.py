# anchorGenerator

# get all the noun phrases and entities and put those as anchors in the database

import nltk
from nltk.corpus import stopwords
from nltk.tree import *
from elasticsearch import Elasticsearch
from nltk.corpus import sentiwordnet as swn
import string
from pprint import pprint
import justext
import time
import datetime

anchors = {}
stop = stopwords.words('english') + list(string.punctuation)
es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)
INDEX  = 'anchors'
TYPES = 'vaccination'
LOGDEX = 'crowdylog'
now = lambda: datetime.datetime.utcnow().isoformat()


query = {
    "query" : {
        "bool" : { 
            "must_not" : {
                "term" : { 
                    "cache.anchors" : True
                }
            }
        }
    },
	"size": 100,
}


# NP patterns   
pattern = r"""
  NP: {<DT|JJ|NN.*>+}          # Chunk sequences of DT, JJ, NN
  PP: {<IN><NP>}               # Chunk prepositions followed by NP
  VP: {<VB.*><NP|PP|CLAUSE>+$} # Chunk verbs and their arguments
  CLAUSE: {<NP><VP>}           # Chunk NP, VP
  """ # define a tag pattern of an NP chunk
NPChunker = nltk.RegexpParser(pattern) # create a chunk parser


def ExtractPhrases( myTree, phrase):
    myPhrases = []
    if (myTree.label()==phrase):
        myPhrases.append( myTree.copy(True) )
    for child in myTree:
        if (type(child) is Tree):
            list_of_phrases = ExtractPhrases(child, phrase)
            if (len(list_of_phrases) > 0):
                myPhrases.extend(list_of_phrases)
    return myPhrases


es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    http_auth=('user', 'aminoglycoside'),
    port=80
)

# gets text from html code
def getText(document):
	paragraphs = justext.justext(document, justext.get_stoplist("English"))
	return ''.join(paragraph.text for paragraph in paragraphs)

# splits text into tagged sentences
def getSentences(text):
	tagged = []
	sentences = nltk.sent_tokenize(text) # NLTK default sentence segmenter
	words = [nltk.word_tokenize(sent) for sent in sentences]
	tagged = [nltk.pos_tag(word) for word in words]
	return tagged

def validKey(key):
	if not all(ord(char) < 128 for char in key):
		return False
	if len(key) <= 1:
		return False
	if key.lower() in stop:
		return False
	if key == '..':
		return False
	else:
		return True

def newAnchor(label,cat):
	return {'count':0, 'label':label, 'cat':cat}

# get noun phrase from a sentence
def getNPs(sentences, anchors):

	for sentence in sentences:
		# noun phrase identification
		chunks = NPChunker.parse(sentence)
		list_of_noun_phrases = ExtractPhrases(chunks, 'NP')
		for np in list_of_noun_phrases:

			label = " ".join(word for word, tag in np)
			# string contains non-ascii characters
			# there should not be single letter anchors
			# string is a stop word
			if validKey(label):
				key = label.lower()+'--NP'
				cat = 'NP'

				#key = " ".join(word+"/"+tag for word, tag in np)
				if key not in anchors:
					anchors[key] = newAnchor(label,cat)
				anchors[key]['count'] += 1
	return anchors


def getNamedEntities(sentences, anchors):

	for sentence in sentences:
		# get named entities in this sentence
		for chunk in nltk.ne_chunk(sentence):
			if type(chunk) is nltk.Tree:
				label = ' '.join(c[0] for c in chunk.leaves())
		
				if validKey(label):
					cat = chunk.label()
					key = label.lower()+'--'+cat
		#					print t,cat
					if key not in anchors:
						#anchors[t] = {'topic':t,'type':cat,'date':date,'retrieved':retrieved,'parent':hit['_id'],'service':hit['_type'],'count':0,'words':0}
						anchors[key] = newAnchor(label,cat)
					anchors[key]['count'] += 1
	return anchors


# get the date it was published, or otherwise when it was retrieved
def getDate(hit):

	if 'retrieved' in hit:
		date = hit['retrieved']		
	elif 'date' in hit:
		date = hit['date']
	else:
		# this should not be possible, but occurs in old data
		date = now()
	return date


# save all data to elasticsearch
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



# main function
if __name__=='__main__':

	body = {
  "size": 0,
  "query": {
    "filtered": {
      "query": {
        "query_string": {
          "query": "*",
          "analyze_wildcard": True
        }
      },
      "filter": {
        "bool": {
          "must": [
            {
              "range": {
                "retrieved": {
                  "gte": 1478853495187,
                  "lte": 1478854395187,
                  "format": "epoch_millis"
                }
              }
            }
          ],
          "must_not": []
        }
      }
    }
  },
  "aggs": {
    "2": {
      "terms": {
        "field": "title",
        "size": 20,
        "order": {
          "_count": "desc"
        }
      }
    }
  }
}
	response = es.search(index="crowdynews", body=query)
	#response = {'hits': { 'hits':[{'_id':'11111','_retrieved':'1-1-2016','_source': {'text': "The man went home."}}]}}

	retrieved = now()

	# go through each retrieved document
	for hit in response["hits"]["hits"]:
		#print hit
		if 'text' in hit['_source'] and len(hit['_source']['text']) > 0:
			doc = hit['_source']['text']
		else:
			continue

		#print doc
		text = getText(doc)
		#print text
		sentences = getSentences(text)
		# get date of this document
		date = getDate(hit['_source'])

		anchors = {}
		# get noun phrases in this sentence
		anchors = getNPs(sentences, anchors)
		# get named entities in this sentence
		anchors = getNamedEntities(sentences, anchors)

		for t in sorted(anchors):
			print hit['_id'],date,t,anchors[t]

		break
			#addBulk(topics)
		#es.update(index = hit['_index'], doc_type=hit['_type'], id=hit['_id'], body = {'doc':{'tagged' : True}})
