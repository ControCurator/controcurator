from elasticsearch import Elasticsearch
es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)
mapping = {
  "mappings": {
    "vaccination": {
      "properties": {
        "topic": {
          "type": "string",
          "index": "not_analyzed"
        },
        "words": {
          "type": "long"
        },
        "count": {
          "type": "long"
        },
        "controversy": {
          "type": "double"
        },
        "service": {
          "type": "string"
        },
        "intensity": {
          "type": "double"
        },
        "parent": {
          "type": "string"
        },
        "negative": {
          "type": "double"
        },
        "type": {
          "type": "string"
        },
        "positive": {
          "type": "double"
        },
        "date": {
          "format": "strict_date_optional_time||epoch_millis",
          "type": "date"
        },
        "retrieved": {
          "format": "strict_date_optional_time||epoch_millis",
          "type": "date"
        }
      }
    }
  }
}

es.indices.create(index='topics', ignore=400, body=mapping)