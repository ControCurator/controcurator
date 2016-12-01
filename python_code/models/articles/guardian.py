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
		article.text = data['response']['content']['blocks']['body'][0]['bodyTextSummary']
		article.service = 'guardianImport'

		article.published = data['response']['content']['blocks']['body'][0]['lastModifiedDate']
		article.retrieved = now()
		article.children = []

		article.updateFeatures()

		# add ControWiki as ground truth
		for anchor in data['response']['content']['ControWiki']:
			if anchor[1] == anchor[1]:
				# check if not NaN
				a = Anchor.getOrCreate(anchor[0])
				a.setGroundTruth('controversy', anchor[1])
				a.save()

		return article