#!/bin/python
'''

This file provides the endpoints for the demo interface.
The functions in this file should be called from NodeJS to
obtain and update datapoints.


Description of functionality
---

data model:
	datapoint = { str(noun phrase) : { 'score': float(controversy score), 'confidence':float(confidence)}}
	estimates = l st(datapoint1, .... , datapointN) 
	labelled  = { str(noun phrase) : { 'label' : 'controversial' OR 'noncontroversial') , 'ip' : str(ip address of user) } }

included endpoints:

GET /controversial 
	returns the estimates for top-10 most and least controversial topics

GET /unsure
	returns a list of datapoints to label

PUT /unsure
	updates model 
	redirects to /controversial (which should yield new ranks)

Usage
---

You can call this script from the commandline and parse the result as json
use the following syntax:

$> endpoints.py <endpoint> [data]

Examples:

$> endpoints.py controversial

OR

$> endpoints.py unsure

OR

$> endpoints.py unsure '[{"Steve Jobs":{"label":"controversial", "ip":""}}]'

Notes on implementation
---

Controversy is labelled on the noun-phrase (here considered topic) level. 
Timestamps should be implemented on the backend side. 

'''
import random # while real data lacks
import json
import sys
import os
#from elasticsearch import Elasticsearch

ELASTIC_CREDENTIALS = '#elastic.json'
ELASTIC_INDEX       = ''

#es = Elasticsearch(**json.load(open(ELASTI_CREDENTIALS)))

### Placeholder functions 
if not 'fake_data.json' in os.listdir('.'):
	nounphrases = ['vaccine', 'research', 'autism', 'flu shots', 'stuff','other stuff', 'trump' , 'projects', 
			 'shopping','Nationale Spoorwegen (NS)', 'government','big pharma','Bill Gates','Steve Jobs',
			'hard work','herd immunity','daily planet', 'NSA','liberty','USA' , 'animal shelters', 
			'labour unions','factory work','Canada','Tourism', 'Flights','pollution'
			'management','NASA','Pluto (planet)']

	fake_data = [{x:{'score':random.betavariate(1,1),'confidence':random.betavariate(1,1)}} for x in nounphrases]
	json.dump(fake_data, open('fake_data.json','w'))
else:
	fake_data = json.load(open('fake_data.json'))

#### End placeholder functions

def controversial(method='GET'):
	'''
	implements the /controversial endpoint. 

	parameters
	----
	none

	returns
	--- 

	{
		controversial    : estimates,
		noncontroversial : estimates
	}
	'''
	datapoints       = sorted(fake_data, key=lambda x : list(x.values())[0].get('score',0))
	controversial    = datapoints[:10]
	noncontroversial = datapoints[10:]
	results = {'controversial':controversial, 'noncontroversial':noncontroversial}
	return json.dumps(results)


def unsure(method='GET', data='[]'):
	'''
	implements the /controversial endpoint. 

	parameters
	----
	data: labelled

	returns
	--- 

	{
		controversial    : estimates,
		noncontroversial : estimates
	}
	'''
	if method == 'GET':
		datapoints       = sorted(fake_data, key=lambda x : list(x.values())[0].get('confidence',0))
		unsure  = datapoints[0]
		results = { 'unsure' : unsure }
		return json.dumps(results)
	else:
		''' expects an object like: {'nounphrase': {'label':'controversial'/'noncrontroversial','ip':'127.0.01'}}'''
		data = json.loads(data)
		if type(data)==dict:
			data = [data]
		global fake_date
		for fdata in fake_data:
			fdatakey = list(fdata.keys())[0]
			fdataval = list(fdata.values())[0]
			update = [list(d.values())[0] for d in data if list(d.keys())[0]==fdatakey]
			if update:
				nscore = update[0].get('labelled','none') == 'controversial' and 1 or 0
				oldscore = fdataval['score']
				fdataval['score'] += (oldscore - nscore) / 5
				fdata = {fdatakey:fdataval}
		json.dump(fake_data, open('fake_data.json','w'))
		return controversial() # hacky hacky redirect-ey

if __name__=='__main__':
	
	if len(sys.argv)==1:
		print(json.dumps({"ERROR":"NO ENDPOINT SPECIFIED"}))
	if len(sys.argv)==2:
		try:
			if sys.argv[1]   == 'controversial': print(controversial())
			elif sys.argv[1] == 'unsure': print(unsure())
			else: print(json.dumps({"404":"Unknown endpoint"}))
			
		except:
			print( json.dumps({'502':'stuff died'}))
	if len(sys.argv)==3:
		try:
			print(unsure(method='PUT', data=sys.argv[2]))
		except:
			raise
			print(json.dumps({'502':'stuff died'}))
