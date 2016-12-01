# import guardian articles
import os
import json
from models.articles.guardian import *

# main function
if __name__=='__main__':

	# load file
	'''
	articles = Guardian.all(size=1000)
	Guardian.delete_all(articles)

	anchors = Anchor.all(size=1000)
	Anchor.delete_all(anchors)
	'''

	directory = '/Users/benjamin/Downloads/controcurator_data_with_wiki/'

	files = os.listdir(directory)
	for file in files[10:]:
		# for each file
		print file
		if file.startswith('.'):
			continue
		with open(directory+file) as f:

			data = json.load(f)
			body = data['response']['content']['blocks']['body'][0]
			#print body['lastModifiedDate']
			print '- ',data['response']['content']['webTitle'].encode('UTF-8')

			article = Guardian.create(data)
			article.save()




			# add comments as article children

