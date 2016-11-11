from elasticsearch import Elasticsearch
es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)
mapping = {
  "mappings": {
    "vaccination": {
      "dynamic_templates": [
        {
          "string_fields": {
            "mapping": {
              "type": "string",
              "fields": {
                "raw": {
                  "index": "not_analyzed",
                  "type": "string"
                }
              }
            },
            "match_mapping_type": "string",
            "match": "*"
          }
        }
      ]
    }
  }
}

es.indices.create(index='anchors', ignore=400, body=mapping)