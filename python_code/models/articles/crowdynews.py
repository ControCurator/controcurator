from ..article import *
from ..anchor import *

import time
import datetime

# crowdynews articles

class CrowdyNews(Article):

	@staticmethod
	def create(data):
		# the current time
		now = lambda: datetime.datetime.utcnow().isoformat()

		article = CrowdyNews()
		article.id = data['id']
		article.url = data['url']
		article.text = data['text']
		article.service = data['service']
		'''article.author = {
			'url' : data['author']['url'],
			'label' : data['author']['name'],
			'image' : data['author']['image']
		}'''

		article.published = data['date']
		article.retrieved = now()
		article.children = []

		article.updateFeatures()

		return article
