'''
Import Guardian articles from JSON
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import json
import re
from urllib import unquote
from elasticsearch import helpers

sys.path.insert(0,'../')
from models.article import Article
from controllers.sentimentExtractor import SentimentExtractor

from elasticsearch import Elasticsearch, ConnectionTimeout
from elasticsearch_dsl.connections import connections
import random
connections.create_connection(hosts=['http://controcurator.org:80/ess'])
es = Elasticsearch(
	['http://controcurator.org/ess/'],
	port=80)

from controllers.guardian_scraper import GuardianScraper
gs = GuardianScraper()



# first we make an index of all social media items and the parents they belong to
# then for each parent we get the social media items of that parent and put them as comment in the article
articlelist = ['https://www.theguardian.com/football/live/2017/apr/11/borussia-dortmund-v-monaco-champions-league-quarter-final-first-leg-live',
'https://www.theguardian.com/business/live/2017/mar/22/markets-tumble-as-impatience-mounts-over-trumps-policies-business-live',
'https://www.theguardian.com/us-news/2017/apr/11/alabama-church-police-force-senate-vote',
'https://www.theguardian.com/uk-news/2017/mar/17/girl-aged-11-to-become-britains-youngest-mother',
'https://www.theguardian.com/music/2017/apr/12/john-geils-jr-founder-of-the-j-geils-band-dies-aged-71',
'https://www.theguardian.com/sport/2017/apr/11/sam-warburton-lions-doubt-knee-injury-six-weeks-rugby-union',
'https://www.theguardian.com/uk-news/2017/apr/11/homeless-man-guilty-of-murdering-hotel-worker',
'https://www.theguardian.com/society/2017/apr/12/two-in-five-gps-in-south-west-of-england-plan-to-quit-survey-finds',
'https://www.theguardian.com/sport/2017/mar/22/usa-japan-world-baseball-classic-semi-final-report',
'https://www.theguardian.com/business/2017/apr/12/tesco-profits-1bn-growth-supermarket',
'https://www.theguardian.com/commentisfree/2017/apr/11/donald-trump-russia-rex-tillersons-visit-syria',
'https://www.theguardian.com/uk-news/2017/mar/21/twins-found-white-cliffs-dover-parents-ashes-muriel-bernard-burgess-scott-enion',
'https://www.theguardian.com/business/2017/apr/11/developing-countries-demands-for-better-life-must-be-met-says-world-bank-head',
'https://www.theguardian.com/football/2017/apr/11/barcelona-neymar-clasico-ban',
'https://www.theguardian.com/politics/2017/apr/12/devon-and-cornwall-pcc-expenses-inquiry-prosecutors',
'https://www.theguardian.com/technology/2017/apr/11/gordon-ramsay-father-in-law-admits-hacking-company-computers',
'https://www.theguardian.com/business/2017/apr/11/trump-china-summit-xi-jinping-business',
'https://www.theguardian.com/science/2017/mar/22/face-medieval-cambridge-man-emerges-700-years-after-death',
'https://www.theguardian.com/us-news/2017/mar/22/donald-trump-president-impeached-liberals-history-process',
'https://www.theguardian.com/books/2017/apr/11/x-men-illustrator-alleged-anti-christian-messages-marvel-ardian-syaf',
'https://www.theguardian.com/business/2017/apr/12/burger-king-ok-google-commercial',
'https://www.theguardian.com/business/2017/apr/12/edf-customers-price-rise-electricity-gas-energy',
'https://www.theguardian.com/football/2017/apr/11/tony-adams-vows-to-give-granada-players-a-kick-up-the-arse',
'https://www.theguardian.com/football/2017/mar/22/football-transfer-rumours-jermain-defoe-back-to-west-ham',
'https://www.theguardian.com/global-development/2017/apr/11/india-acts-to-help-acid-attack-victims',
'https://www.theguardian.com/tv-and-radio/2017/mar/22/in-your-face-david-attenborough-grayson-perry-takes-home-rts-awards',
'https://www.theguardian.com/world/2017/mar/18/mafia-godfather-banned-bishop-sicily-michele-pennisi',
'https://www.theguardian.com/commentisfree/2017/apr/11/france-left-europe-jean-luc-melenchon-presidential-election',
'https://www.theguardian.com/commentisfree/2017/apr/11/sean-spicers-hitler-holocaust-speak-volumes',
'https://www.theguardian.com/football/2017/apr/11/borussia-dortmund-shock-team-bus-explosions',
'https://www.theguardian.com/football/2017/mar/22/which-football-manager-has-been-sacked-by-one-club-the-most-times',
'https://www.theguardian.com/sport/2017/apr/11/pennsylvania-woman-jail-threats-youth-football-league-officials',
'https://www.theguardian.com/sport/2017/apr/12/afl-players-expecting-bumper-new-pay-offer-as-end-to-dispute-nears',
'https://www.theguardian.com/sport/2017/apr/12/mark-cavendish-diagnosed-epstein-barr-virus-cycling',
'https://www.theguardian.com/sport/blog/2017/mar/22/talking-horses-best-wednesday-bets-for-warwick-and-newcastle',
'https://www.theguardian.com/uk-news/2017/apr/11/boris-johnson-full-support-failure-secure-sanctions-syria-russia',
'https://www.theguardian.com/world/2017/mar/22/brussels-unveil-terror-victims-memorial-one-year-after-attacks',
'https://www.theguardian.com/business/2017/mar/22/nervous-markets-take-fright-at-prospect-of-trump-failing-to-deliver',
'https://www.theguardian.com/commentisfree/2016/dec/21/i-lost-my-mum-seven-weeks-ago-our-readers-on-coping-with-grief-at-christmas',
'https://www.theguardian.com/fashion/2017/mar/22/fiorucci-why-the-disco-friendly-label-is-perfect-for-2017',
'https://www.theguardian.com/law/2017/apr/12/judge-sacked-over-online-posts-calling-his-critics-donkeys',
'https://www.theguardian.com/society/2017/apr/11/national-social-care-service-centralised-nhs',
'https://www.theguardian.com/sport/2017/apr/12/gb-team-pursuit-world-track-cycling-championships-bronze',
'https://www.theguardian.com/sport/2017/mar/17/toronto-london-broncos-challenge-cup-hull-fc-widnes-leeds-wakefield-super-league',
'https://www.theguardian.com/sport/2017/mar/22/nfl-game-speed-changes-officiating-fewer-commercials-roger-goodell',
'https://www.theguardian.com/sport/2017/mar/22/taumalolo-becomes-one-of-richest-players-in-rugby-league-with-10m-cowboys-deal',
'https://www.theguardian.com/tv-and-radio/2017/mar/22/n-word-taboo-tv-carmichael-show-atlanta-insecure-language',
'https://www.theguardian.com/us-news/2017/mar/22/fbi-muslim-employees-discrimination-religion-middle-east-travel',
'https://www.theguardian.com/us-news/2017/mar/22/zapier-pay-employees-move-silicon-valley-startup',
'https://www.theguardian.com/world/2017/mar/22/gay-clergyman-jeffrey-johns-turned-down-welsh-bishop-twice-before-claims',
'https://www.theguardian.com/world/2017/mar/22/israel-whisky-gin-bottles-first-world-war',
'https://www.theguardian.com/world/2017/mar/23/apple-paid-no-tax-in-new-zealand-for-at-least-a-decade-reports-say',
'https://www.theguardian.com/books/2017/mar/22/comics-chavez-redline-transformers-v-gi-joe',
'https://www.theguardian.com/business/2017/apr/11/uk-inflation-rate-stays-three-year-high',
'https://www.theguardian.com/commentisfree/2017/apr/12/charlie-gard-legal-aid',
'https://www.theguardian.com/commentisfree/2017/mar/22/rights-gig-economy-self-employed-worker',
'https://www.theguardian.com/lifeandstyle/2017/mar/22/using-the-pill-can-protect-women-from-certain-cancers-for-up-to-30-years',
'https://www.theguardian.com/music/2017/apr/11/michael-buble-wife-says-son-noah-is-recovering-from-cancer',
'https://www.theguardian.com/society/2017/apr/11/are-you-a-scout-or-scout-leader-tell-us-your-story',
'https://www.theguardian.com/society/2017/apr/11/bullying-and-violence-grip-out-of-control-guys-marsh-jail-dorset',
'https://www.theguardian.com/sport/2017/apr/11/boston-celtics-no1-seed-nba-eastern-conference-cleveland-cavaliers',
'https://www.theguardian.com/stage/2017/mar/22/trisha-brown-obituary',
'https://www.theguardian.com/us-news/2017/apr/11/us-universal-healthcare-single-payer-rallies',
'https://www.theguardian.com/us-news/2017/apr/12/manchester-by-the-sea-inspired-couple-kill-son-house-fire',
'https://www.theguardian.com/us-news/2017/mar/17/hillary-clinton-ready-to-return-politics',
'https://www.theguardian.com/us-news/2017/mar/22/us-border-agent-sexually-assaults-teenage-sisters-texas',
'https://www.theguardian.com/world/2017/apr/11/hundreds-of-refugees-missing-after-dunkirk-camp-fire',
'https://www.theguardian.com/world/2017/mar/22/unicef-condemns-sale-cambodian-breast-milk-us-mothers-firm-ambrosia-labs']

query = {
  "query": {
    "bool": {
      "must_not": [
        {
          "term": {
            "source": "vaccination"
          }
        },
        {
          "constant_score": {
            "filter": {
              "missing": {
                "field": "parent.url"
              }
            }
          }
        },
        {
          "constant_score": {
            "filter": {
              "missing": {
                "field": "source"
              }
            }
          }
        }
      ]
    }
  },
  "from": 10000,
  "size": 10000
}
query = {
  "query": {
    "bool": {
      "must": [
        {
          "term": {
            "parent.url": "controcuratorguardian"
          }
        }
      ],
      "must_not": [],
      "should": []
    }
  },
  "from": 0,
  "size": 10000
}
downloaded = {}


response = es.search(index="crowdynews", body=query)

data = response['hits']['hits']
actions = []

for socmed in data:

	url = unquote(re.sub('\/v1\/(.*[a-z])\/controcuratorguardian\?q=','',str(socmed['_source']['parent']['url']),))

	if url not in articlelist:
		print "NOT INTERESTING"#, NEXT"
		#continue


	print url
	
	query = {
	  "query": {
		"constant_score": {
		  "filter": {
			"term": {
			  "url": url
			}
		  }
		}
	  },
	  "from": 0,
	  "size": 1
	}


	response = es.search(index="controcurator", doc_type="article", body=query)
	if len(response['hits']['hits']) == 0:
		print "ARTICLE NOT FOUND"

		if url not in downloaded:
			guardianresult = gs.retrieveArticle(url,True)[0]
			downloaded[url] = guardianresult
			print "DOWNLOADED"
		else:
			guardianresult = downloaded[url]
			print "FOUND IN CACHE"

		if not guardianresult:
			print "ARTICLE HAS NO CONTENT, NEXT"
			continue

		body = guardianresult['response']['content']['blocks']['body'][0]
		id = guardianresult['response']['content']['blocks']['body'][0]['id']
		url = guardianresult['response']['content']['webUrl']
		dtype = guardianresult['response']['content']['type']
		if dtype <> 'article':
			print "NOT AN ARTICLE, NEXT"
			continue

		# try to find thumbnail
		# thumb = data['response']['content']['blocks']['body'][0]['elements']
		webtitle = guardianresult['response']['content']['webTitle'].encode('UTF-8').split(' | ')[0]
		section = guardianresult['response']['content']['sectionId']
		pubdate = guardianresult['response']['content']['webPublicationDate']
		comments = guardianresult['response']['content']['blocks']['comments']
		try:
			print len(comments)
		except TypeError:
			comments = {}

		if len(comments) < 10:
			print "TOO FEW COMMENTS",len(comments)
			continue

		if len(comments) > 1000:
			print "MANY COMMENTS",len(comments)
			#continue


		html = guardianresult['response']['content']['blocks']['body'][0]['bodyHtml'].decode('ascii', 'ignore')
		paragraphs = html.split('</p>')
		stripHtml = lambda text: re.compile('(?!<p>|<br>|<br />)<.*?>').sub('', text)
		text = u'</p>'.join([stripHtml(p) for p in paragraphs]) + '</p>'

		article = Article(meta={'id': id})
		print id
		article.url = url
		article.type = "article"
		article.source = "crowdynews"
		article.published = pubdate
		article.document = {"title": webtitle, 'text': text}
		

		newcomments = []
		for comment in comments:
			if comment['reply-to'] == "":
				comment['sentiment'] = SentimentExtractor.getSentiment(comment['text'])
				newcomments.append(comment)
				print "COMMENT SAVED"
		article.comments = newcomments
		article.features = {"controversy": {"random": random.random()},"socmed":len(newcomments)}


		try:
			article.save(index='controcurator')
			print "SAVED ARTICLE"
		except ConnectionTimeout:
			es = Elasticsearch(['http://controcurator.org/ess/'],port=80)
			article.save(index='controcurator')
			print "SAVED ARTICLE"

		# reload article from database
		query = {
		  "query": {
			"constant_score": {
			  "filter": {
				"term": {
				  "url": url
				}
			  }
			}
		  },
		  "from": 0,
		  "size": 1
		}

		response = es.search(index="controcurator", doc_type="article", body=query)

	if len(response['hits']['hits']) == 0:
		print "ERROR: ARTICLE WAS NOT DOWNLOADED, NEXT"
		continue

	article = response['hits']['hits'][0]
	print "ARTICLE FOUND IN DB"

	if 'comments' not in article['_source']:
		print "ARTICLE HAS NO COMMENTS"
		article['_source']['comments'] = []

	comment_ids = [comment['id'] for comment in article['_source']['comments']]
	if socmed['_source']['id'] in comment_ids:
		print "EXISTING SOCMED, NEXT"
		continue

	comment = {
	"author-id": socmed['_source']['author']['userid'],
	"author": socmed['_source']['author']['name'],
	"type" : socmed['_source']['service'],
	"timestamp": socmed['_source']['date'],
	"reply-to": "",
	"id": socmed['_source']['id'],
	}

	if 'raw_text' in socmed['_source']:
		comment["text"] = socmed['_source']['raw_text']
	else:
		comment["text"] = socmed['_source']['text']

		
	comment['sentiment'] = SentimentExtractor.getSentiment(comment['text'])
	article['_source']['comments'].append(comment)



	Article.get(id=article['_id']).update(comments=article['_source']['comments'])
	print 'COMPLETED',article['_id']







