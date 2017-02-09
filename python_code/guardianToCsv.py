# take the guardian articles and generate a csv

# import guardian articles
import os
import json
import csv
from models.articles.guardian import *

# main function
if __name__=='__main__':

	directory = '/Users/benjamin/Downloads/controcurator_data_with_wiki/'
	files = os.listdir(directory)

	fieldnames = ['id','url','title','paragraphCount','text','commentCount','comments']

	# write to csv file
	w = open('guardian.csv', 'wb')
	wr = csv.writer(w, delimiter=',',quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
	wr.writerow(fieldnames)

	# keep track of how many articles are used
	count = 0

	# go through each file
	for file in files:

		# ignore system files
		if file.startswith('.'):
			continue

		# read file contents
		with open(directory+file) as f:

			# read the JSON content
			data = json.load(f)

			# content
			body = data['response']['content']['blocks']['body'][0]
			id = data['response']['content']['blocks']['body'][0]['id']
			url = data['response']['content']['webUrl']
			webtitle = data['response']['content']['webTitle'].encode('UTF-8').split(' | ')

			# sometimes the name of the author is in the title, so we take that out
			title = webtitle[0]


			html = data['response']['content']['blocks']['body'][0]['bodyHtml']
			# find comments
			comments = data['response']['content']['blocks']['comments']

			# for now take only articles that have more than five comments
			if not comments:
				print 'SKIPPED:',title
				continue

			# also skip the article if less then 5 comments are available
			# ignore comments that are replies to other comments
			# ignore comments of which the content was moderated
			selectedComments = [c['text'] for c in [comment for comment in comments if comment['reply-to'] == '' and not comment['text'].startswith('This comment was removed')][0:5]]
			if len(selectedComments) < 5:
				print 'SKIPPED:',title
				continue

			# take the first two paragraphs and remove all html tags except for <br> and <p>
			paragraphs = html.split('</p>')
			paragraphCount = len(paragraphs)
			stripHtml = lambda text: re.compile('(?!<p>|<br>|<br />)<.*?>').sub('',text)
			text = '</p>'.join([stripHtml(p) for p in paragraphs[:2]])+'</p>'

			# array for one row on the csv
			row = [
				id,
				url,
				title,
				paragraphCount,
				text.encode('UTF-8'),
				commentCount,
				'||'.join(selectedComments).encode('UTF-8')
			]

			print 'SAVED:',title
			wr.writerow(row)
			count += 1

		if count >= 100:
			break

	w.close()




