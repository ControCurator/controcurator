from elasticsearch import Elasticsearch

# connection to elasticsearch
es = Elasticsearch(['http://controcurator.org/ess/'],port=80)

# query to retrieve articles from the database
# this should be updated later to only retrieve articles that do not have a score yet
query = {
    "query": {
        "bool": {
            "must": {
                "match_all": {}
            }
        }
    },
    "from": 0,
    "size": 10
}

# request to the database
request = es.search(index='controcurator',doc_type='article',body=query)

# loop through each retrieved article
for article in request['hits']['hits']:

    # the identifier of this article
    id = article['_id']
    print id

    # the set of comments
    comments = article['_source']['comments']
    
    # EXAMPLE COMMENT
    '''
    {
    "author-id": "4096454",
    "sentiment": {
            "sentences": 2,         ## = number of sentences
            "words": 1,             ## = number of sentiment words
            "positivity": 0.5,      ## = sum of all positive sentiment
            "negativity": 0.125,    ## = sum of all negative sentiment
            "sentiment": 0.375,     ## = (positivity - negativity) / words
            "intensity": 0.625      ## = (positivity + negativity) / words
 
            },
        "author": "UnevenSurface",
        "timestamp": "2016-11-27T06:23:04+00:00",
        "text": "Ha! Instantly reminded me of the Two Ronnies classic, You're Nuts, M'Lord.",
        "reply-to": "",             ## only root comments have sentiment now, so this should always be empty
        "id": "88296138"
    }
    '''

    # CLASSIFIER

    # controversy score for this article
    score = 0

    # update query
    body = {"doc": {"features": {"controversy": {"value" : score }}}}
    #es.update(index='controcurator',doc_type='article',id=id,body=body)



