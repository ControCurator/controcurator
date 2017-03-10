from __future__ import division
import sys
from optparse import OptionParser
from bs4 import BeautifulSoup
from tqdm import tqdm
import requests
import codecs
import time
import datetime
import json
import urllib
import requests
import os
from string import replace



class GuardianScraper:
	def __init__(self,json_input='../controllers/key.json'):

		'''__init__ takes as input a json file, which defines the parameters of the search'''
		self.json_input = json.load(open(json_input,'r'))
		
		
		#self.saveto = 'data'
		
		#if os.path.isdir(self.saveto) == False:
		#	os.mkdir(self.saveto)


	def retrieveArticle(self,url,collect_comments):
		'''
		given a url, this method makes a call to the Guardian 
		api and retrieves the article in json format
		if the parameters collect_comments is set to True, 
		it will also scrape the comments using the
		"scrapeComments" script. 
		'''

		'''prepare call to the Guardian api to retrieve a single article'''
		params = ['api-key','show-blocks']
		api_url = url.strip() + '?' + '&'.join(
										[
											k+'='+v for k,v in self.json_input.items() 
												if k in params
													]
												)
		api_url = api_url.replace('www.theguardian.com','content.guardianapis.com')

		page = requests.get(api_url).json()

		'''
		page id is a unique reference for each article
		these ids will be used later as filename for each article downloaded	
		'''
		# Added a quick hack here to prevent the script from crashing
		try:
			#page_id = page['response']['content']['blocks']['body'][0]['id']
			page_id = ''.join([ch for ch in page['response']['content']['id'] if ch.isalpha()])
		except:

			print 'File with API URL \n%s\n has no ID, return None'%api_url
			return None,None

		'''proceeding with collecting comment is collect_comments is set to True'''
		if collect_comments:
			'''comments only available on the original article page, rewrite api-url as the normal html url'''
			html_url = url.replace('https://content.guardianapis.com/','https://www.theguardian.com/')
			#print('Downloading comments for {}'.format(html_url))

			'''call scrapeComments to retrieving comments. script should be save in the folder'''
			comments = scrapeComments(html_url)

			'''add comments to the json file'''
			page['response']['content']['blocks']['comments'] = comments

		return page,page_id



	def scrapeUrls(self,urls,collect_comments=True):
		'''this method reads the list with url and collect information for each'''
		
		if os.path.isdir(self.saveto) == False:
			os.mkdir(self.saveto)

		'''because this script is made to download content'''
		self.json_input["show-blocks"] = "all"


		for url in tqdm(urls, total=len(urls)): 
			time.sleep(0.0001)

				
			page,id = self.retrieveArticle(url,collect_comments=collect_comments)
			# Added a quick hack to prevent the script from crashing
			if page == None: continue
			article_path = os.path.join(self.saveto,'{}.json'.format(id))
			
			with open(article_path, 'w') as out:
				json.dump(page, out)

def getHTML(url):
    for i in range(0,10):
        while True:
            try:
                html = urllib.urlopen(url).read()
                #html= requests.get(url)
            except Exception as e:
                print(e)
                continue
            break
    
    return BeautifulSoup(html,'lxml')

'''still under construction. script needs to be optimized from here'''
def scrapeComments(url):
    articleSoup = getHTML(url)
    try:
    	articleTitle = articleSoup.find('h1', class_="content__headline").getText().strip().encode('utf-8')
    	commentUrl = articleSoup.find(class_='discussion__heading').find('a')['href']
    except AttributeError:
        #print("Article doesn't contain comments. Proceeding to next.")
        return None 

    #print 'Finding comments for [{0}]({1})\n'.format(articleTitle, url)

    commentSoup = getHTML(commentUrl)

    paginationBtns = commentSoup.find_all('a', {'class':'pagination__action'})
    LastPaginationBtn = commentSoup.find('a', {'class':'pagination__action--last'})

    if LastPaginationBtn is not None:
        totalPages = int(LastPaginationBtn['data-page'])
    elif paginationBtns:
        totalPages = int(paginationBtns[-1]['data-page'])
    else:
        totalPages = 1

    def getComments(url):
        soup = getHTML(url)
        #print 'Fetching {0}'.format(url)
        commentArray = []
        for comment in soup.select('li.d-comment'):
            commentObj = {}
            commentObj['id'] = comment['data-comment-id']
            commentObj['timestamp'] = comment['data-comment-timestamp']
            commentObj['author'] = comment['data-comment-author'].encode('utf-8')
            commentObj['author-id'] = comment['data-comment-author-id']
            # commentObj['reccomend-count'] = comment.find(class_='d-comment__recommend')['data-recommend-count']

            body = comment.find(class_='d-comment__body')
            if body.blockquote is not None:
                body.blockquote.clear()
            commentObj['text'] = body.getText().strip().encode('utf-8')

            replyTo = comment.find(class_='d-comment__reply-to-author')
            if replyTo is not None:
                link = replyTo.parent['href'].replace('#comment-', '')
                commentObj['reply-to'] = link
            else:
                commentObj['reply-to'] = ''

            commentArray.append(commentObj)
        commentArray = commentArray[::-1]
        return commentArray

    allComments = []

    #for i in range(totalPages, 0, -1):
    for i in tqdm(range(totalPages, 0, -1)):
        params = urllib.urlencode({'page': i})
        url = '{0}?={1}'.format(commentUrl, params)
        pageComments = getComments(url)
        allComments = allComments + pageComments
    return allComments


if __name__=='__main__':
	parser = OptionParser()
	parser.add_option("-c", "--comments",
							type='int',
							dest="comments",
                			help="binory argument [0|1]. Determines to include comments or not",
                			default=1)

	options, args = parser.parse_args()
	scraper = GuardianScraper()

	urls = ['https://content.guardianapis.com/world/2016/oct/19/home-office-expected-to-speed-up-rescue-of-migrant-children-from-calais',
	'https://content.guardianapis.com/commentisfree/2016/jul/05/you-think-autistic-people-have-no-empathy-my-little-boy-is-so-empathetic-it-hurts',
	'https://content.guardianapis.com/social-care-network/social-life-blog/2016/oct/19/social-workers-challenge-exclusion-system-work-better']

	scraper.scrapeUrls(urls,collect_comments=options.comments)

	
	

