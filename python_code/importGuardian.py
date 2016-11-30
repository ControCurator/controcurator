# import guardian articles
import os
import json
from models.articles.guardian import *

# main function
if __name__=='__main__':

	anchors = Guardian.all(size=1000)
	Guardian.delete_all(anchors)

	# load file
	directory = '/Users/benjamin/Downloads/source_GuardianandWiki/'

	files = os.listdir(directory)
	for file in files:
		# for each file
		print file

		with open(directory+file) as f:

			data = json.load(f)
			body = data['response']['content']['blocks']['body'][0]
			print body['lastModifiedDate']
			print data['response']['content']['webTitle'].encode('UTF-8')

			article = Guardian.create(data)
			article.save()

		break

		# add article


			# add comments as article children


		# add wiki topics as anchors
		'''
		for anchor in anchors:
			a = Anchor.getOrCreate('guardian-import', anchor.lower(), anchor)
			a.findInstances()
			a.save()
		'''
		
		#print added article.id