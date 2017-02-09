# anchorGenerator
from models.anchor import *

# main function
if __name__=='__main__':


	# TEMP: Wipe existing anchors
#	anchors = Anchor.all(size=1000)
#	Anchor.delete_all(anchors)

	# THIS IS TEMPORARY:
	anchors = {'Vaccination', 'Vaccinations', 'Vaccine', 'Vaccines', 'Inoculation', 'Immunization', 'Shot', 'Chickenpox', 'Disease', 'Diseases', 'Hepatitis A', 'Hepatitis B', 'infection', 'infections', 'measles', 'outbreak', 'mumps', 'rabies', 'tetanus', 'virus', 'autism'}
	seed = 'vaccination'

	for anchor in anchors:
		a = Anchor.getOrCreate(anchor)
		a.findInstances()
		a.save()





	"""
	query = {
  "size": 0,
  "query": {
    "filtered": {
      "query": {
        "query_string": {
          "query": "*",
          "analyze_wildcard": True
        }
      }
    }
  },
  "aggs": {
    "2": {
      "terms": {
        "field": "title",
        "size": 100,
        "order": {
          "_count": "desc"
        }
      }
    }
  }
}

	response = es.search(index="crowdynews"', 'body=query)

	retrieved = now()
	anchors = {}
	# go through each retrieved document
	for hit in response['aggregations']['2']['buckets']:

		key = hit['key']
		if validKey(key):
			anchors[key] = hit['doc_count']

	addBulk(anchors)
	"""