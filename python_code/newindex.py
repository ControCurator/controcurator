from elasticsearch_dsl import Mapping, Date, Nested, String
from elasticsearch import Elasticsearch

es = Elasticsearch(
	['http://controcurator.org/ess/'],
	port=80)

m = Mapping('document')
m.field('source', String(index='not_analyzed'))
m.field('type', String(index='not_analyzed'))
m.field('parent', String(index='not_analyzed'))
m.field('url',String(index='not_analyzed'))
m.field('published', Date())

docfield = Nested()
docfield.field('title',String(index='analyzed'))
docfield.field('image',String(index='not_analyzed'))
docfield.field('text',String(index='analyzed'))
docfield.field('author',String(index='analyzed'))

m.field('document',docfield)

featfield = Nested()
featfield.field('quality',Nested())
featfield.field('controversy',Nested())
featfield.field('author',Nested())
featfield.field('kudos',Nested())

m.field('features',featfield)

m.save('controcurator',es)


#hallo