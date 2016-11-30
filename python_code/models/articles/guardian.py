# creates guardian article
from ..article import *
from ..anchor import *
import time
import datetime

# a guardian specific type article
class Guardian(Article):

	@staticmethod
	def create(data):
		# the current time
		now = lambda: datetime.datetime.utcnow().isoformat()

		article = Guardian()
		article.id = data['response']['content']['blocks']['body'][0]['id']
		article.url = data['response']['content']['webUrl']
		article.title = data['response']['content']['webTitle']
		article.body = data['response']['content']['blocks']['body'][0]['bodyHtml']
		article.text = data['response']['content']['blocks']['body'][0]['bodyTextSummary']
		article.service = 'guardianImport'

		article.published = data['response']['content']['blocks']['body'][0]['lastModifiedDate']
		article.retrieved = now()
		article.children = []

		article.updateFeatures()

		for anchor in data['response']['content']['ControWiki']:
			a = Anchor.getOrCreate(anchor[0].lower(), anchor[0])
			a.setGroundTruth('controversy', anchor[1])
			a.save()

		return article