from __future__ import division
import sys
from optparse import OptionParser
from bs4 import BeautifulSoup
import requests
import codecs
import time
import datetime
import json
import urllib
import requests
import os


'''
This script retrieves the content, and if requested related blog posts, of articles on The Guardian.
It reads as input a json file, in which all parameters are defined.
The filename (<query_id>.json) serves as an ID for the query. All data is stored in <query_id>_data

Example usage python guardianScraper.py [input_json] --resume=[0|1] --comments=[0|1] --operation=[collect|retrieve|all] --max=100

e.g. python controguardian.py immigration.json --resume=1 --comments=0 --operation=all --max=50

--max: the maximum number of articles to retrieve. maximum is 5000 per day.

--comments: include comments (or not)

--resume: resume scraper where previous run has stopped.

--options: select type of operation.

	collect: retrieve all the urls from the Guardian API that match the given query. Script saves the urls in <query_id>_apiurls
	
	retrieve: given a list of urls, stored in <query_id>_apiurls, this method iteratures over the list 
	and retrieves each article. 
	articles are saved in json formet in the folder <query_id>_data/source. the filename is the unique id of the article.
	this scripts keeps a log file in the urls of the downloaeded articles are stored.
	
	all: call both collect and retrieve


Example of JSON input:

{
	"page-size": "50", 
	"from-date": "2016-01-01", 
	"api-key": "Lalala", 
	"q": "immigration OR refugee OR asylum", 
	"page=": "", 
	"order-by":"newest"
	}

'''

class GuardianScraper:
	def __init__(self,json_input):
		'''__init__ takes as input a json file, which defines the parameters of the search'''
		self.json_input = json.load(open(json_input,'r'))
		
		
		'''save the name of the json file, makes it easier later on the recognize the different stages of the query'''
		self.query_name = json_input.split('/')[-1][:-5]
		self.saveto = self.query_name + '_data'
		
		if os.path.isdir(self.saveto) == False:
			os.mkdir(self.saveto)

	def collectUrls(self,maxArticles):
		'''
		This function collects all urls based on parameters defined in json_input.
		Parameters will be appended to baseUrl.
		These urls will be stored in a separate which can be fed to the retrieveArticles method.
		'''
		baseUrl = 'http://content.guardianapis.com/search?'

		'''check if parameters contain an api-keys'''
		if not self.json_input.has_key('api-key'): raise Exception('JSON file needs an api-key.')

		'''searches can be over multiple pages. if no page parameter set, add it to the json file'''
		if not self.json_input.has_key('page'): self.json_input['page'] = 1

		'''because this script is made to download content'''
		self.json_input["show-blocks"] = "all"

		'''store the output in the separate file'''
		outputUrls = codecs.open(os.path.join(self.saveto,self.query_name+'_apiurls'),'w',encoding='utf-8')

		'''
		iterate over all the pages, which is equal to the the maximum number of hits
		divided by the number pages per call to the api
		'''
		api_urls = []
		page_number = 1

		while len(api_urls) <= maxArticles:
			'''
			page parameter is equal to the turn in the iteration
			'''
			self.json_input['page']=page_number

			'''create call to the api to retrieve the article'''
			url = baseUrl + '&'.join([str(k)+'='+str(v) for k,v in self.json_input.items()])
			response = requests.get(url).json()
			try:
				'''
				TO DO: Find a more elegant way for limiting the number of article to retrieve
				try to scrape as far as the guardian allows you. 
				if number of pages for a give query is exceeded, this will raise a KeyError
				'''
				print('Collecting urls at page %s.\n%0.2f per cent of api-urls retrieved' % (response['response']['currentPage'],len(api_urls)/maxArticles))
			except KeyError:
				break
			page_urls = [
					article['apiUrl'] 
						for article in response['response']['results']
							]
			api_urls.extend(page_urls)
			
			page_number+=1


		outputUrls.write(u'\n'.join(api_urls))


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


		page = requests.get(api_url).json()
		'''
		page id is a unique reference for each article
		these ids will be used later as filename for each article downloaded	
		'''
		page_id = page['response']['content']['blocks']['body'][0]['id']

		'''proceeding with collecting comment is collect_comments is set to True'''
		if collect_comments:
			'''comments only available on the original article page, rewrite api-url as the normal html url'''
			html_url = url.replace('https://content.guardianapis.com/','https://www.theguardian.com/')
			print 'Downloading comments for {}'.format(html_url)

			'''call scrapeComments to retrieving comments. script should be save in the folder'''
			comments = scrapeComments(html_url)

			'''add comments to the json file'''
			page['response']['content']['blocks']['comments'] = comments

		return page,page_id



	def scrapeUrls(self,collect_comments=True,resume=True):
		'''this method reads the list with url and collect information for each'''
		repository = os.path.join(self.saveto,'source')
		
		if os.path.isdir(repository) == False:
			os.mkdir(repository)

		'''because this script is made to download content'''
		self.json_input["show-blocks"] = "all"

		
		logPath = os.path.join(self.saveto,self.query_name + '_log')

		if os.path.isfile(logPath) == False:
			'''
			resume works if there is a log file with scraped urls
			override parameter in case this file doesn't exist
			'''
			resume = False

		if resume:
			'''get the urls of the scraped articles saved in the log file'''
			log = open(logPath,'r')
			scraped = set(log.read().split('\n'))
			log.close()
		
		log = open(logPath,'a')
		
		urlFile = os.path.join(self.saveto,self.query_name + '_apiurls')

		for url in open(urlFile).read().splitlines():
					
				if (resume and url not in scraped) or (not resume):
					log.write(url+'\n')
					print "Scraping, currently at {}".format(url)
					page,id = self.retrieveArticle(url,collect_comments=collect_comments)
					article_path = os.path.join(repository,'{}.json'.format(id))
					with open(article_path, 'w') as out:
						json.dump(page, out)
						time.sleep(1)
				else:
					print 'Already scraped %s. Continue.'%url
		
		log.close()

def getHTML(url):
    for i in range(0,10):
        while True:
            try:
                html = urllib.urlopen(url).read()
                #html= requests.get(url)
            except Exception as e:
                print e
                continue
            break
    
    return BeautifulSoup(html)

'''still under construction. script needs to be optimized from here'''
def scrapeComments(url):
    articleSoup = getHTML(url)
    articleTitle = articleSoup.find('h1', class_="content__headline").getText().strip().encode('utf-8')
    try:
        commentUrl = articleSoup.find(class_='discussion__heading').find('a')['href']
    except AttributeError:
        print("Article doesn't contain comments. Proceeding to next.")
        return None 

    print 'Finding comments for [{0}]({1})\n'.format(articleTitle, url)

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
        print 'Fetching {0}'.format(url)
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

    for i in range(totalPages, 0, -1):
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
                			default=0)

	parser.add_option("-r", "--resume", 
							type='int',
							dest="resume",
                			help="binory argument [0|1]. If set to '1' the script resumes where previous scraping turn has stopped.",
                			default=1)

	parser.add_option("-m", "--max",
						type='int',
                  		dest="maxArticles",
                  		default=100,
                  		help="Integer, indicates the maximun number of articles to retrieve.")

	parser.add_option("-o", "--operation",
						type='string',
                  		dest="operation",
                  		default='all',
                  		help="Type of operation to select. Options are [collect|retrieve|all].")
	
	options, args = parser.parse_args()
	scraper = GuardianScraper(args[0])

	if options.operation == 'collect':
		scraper.collectUrls(options.maxArticles)
	
	elif options.operation == 'retrieve':
		scraper.scrapeUrls(collect_comments=options.comments,resume=options.resume)
	
	elif options.operation == 'all':
		scraper.collectUrls(options.maxArticles)
		scraper.scrapeUrls(collect_comments=options.comments,resume=options.resume)



