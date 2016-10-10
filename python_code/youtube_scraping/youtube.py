#!/bin/python
'''
Retrieve Youtube video *information*

'''

import requests
import elasticsearch
import json
import logging
from requests import ConnectTimeout, ConnectionError
import httplib2
import os
import datetime

from apiclient import discovery
from oauth2client import client
from oauth2client.client import Credentials

logger = logging.getLogger(__name__)
logging.basicConfig(level='INFO')

TIMEOUT     = 20 # allowed request timeout in seconds
APP_NAME    = 'youtube api consumer'
API_KEYFILE = '#api_key.json'  # should be a file in this directory containing a single string
OAUTH_FILE  = '#credentials.json' # file that contains a serialized http_auth object 
CLIENT_FILE = "#client_secrets.json" # client secrets file downloaded from the app oauth page
IGNORE_ERRORS = True

try: 
	API_KEY = json.load(open(API_KEYFILE))
except:
	print("please get a YouTube DATA-API key from https://console.developers.google.com/ ")
	print()
	print("1) Which API are you using? => Pick 'YouTube Data API v3 ")
	print("2) Where will you be calling the API from? => 'Other non-UI (e.g. cron job, deamon)'")
	print("3) What data will you be accessing? => 'Public data'")
	print("4) click 'what credentials do I need?")
	print()
	print('fill in the key displayed there\n')
	API_KEY = input("key: ").strip()
	json.dump(API_KEY, open(API_KEYFILE,'w'))

now = lambda : datetime.datetime.now().isoformat()

def setup_oauth(nosave=False):
	'''
	Sets up OAuth for protected resources, such as captions. 

	Requires client key and secret file called 'client_secrets.json' in this directory. 
	You can obtain the contents of this file by enabeling OAuth authentication
	at the app settings page found at 'https://console.developers.google.com/'

	
	'''
	
	print(setup_oauth.__doc__)
	
	flow = client.flow_from_clientsecrets(
	    CLIENT_FILE,
	    scope="https://www.googleapis.com/auth/youtube.force-ssl",
	    redirect_uri='urn:ietf:wg:oauth:2.0:oob')

	auth_uri = flow.step1_get_authorize_url()
	
	print("Please visit\n\n %s \n\nfor your authentication code. (you may be able to ctrl-click the link)"%auth_uri)

	auth_code = input('Enter the auth code: ')

	credentials = flow.step2_exchange(auth_code)
	with open(OAUTH_FILE,'w') as f:
		f.write(credentials.to_json())
	
	http_auth = credentials.authorize(httplib2.Http())
	
	return http_auth

def get_oauth():
	try:
		logger.info("using existing OAuth credentials")
		credentials = Credentials.new_from_json(open(OAUTH_FILE,'r').read())
		http_auth = credentials.authorize(httplib2.Http())
	except:
		http_auth = setup_oauth()
	return http_auth

def reset_oauth():
	logger.info("removing and resetting oauth")
	os.remove(OAUTH_FILE)
	setup_oauth()

def get(url, params=None, data=None, retries=3, timeout=20, oauth=False):
	'''
	This function wraps requests.get to handle the YouTube API specific error codes that may pop up.
	'''
	ignore_errors = IGNORE_ERRORS
	try:
		if oauth: 
			http_auth = get_oauth()
			response = http_auth.request(url, 'GET', headers=params)
			if type(response)==tuple: return response[1].decode('utf-8','ignore') # ugly but find; TODO
		else:
			response = requests.get(url,params=params, data=data, timeout=TIMEOUT)
		if response.status_code==200: 
			return response.json()
		elif response.status_code == 404 :
			logger.info("No items found for {data}".format(**locals))
			return {} 
		elif response.status_code == 400 : 
			if not ignore_errors:
				raise Exception("Bad Request: you probably have incorrect parameter (values), refer to the API documentation")
			else:
				logger.warn("400 exception!")
				return {}
		elif response.status_code == 403 :
			if not ignore_errors:
				raise Exception("Forbidden status code (403): your API Key is wrong or your options require OAuth! (not supported here)")
			else:
				logger.warn('403: forbidden')
				return {'status':'forbidden'}
		elif response.status_code == 401 :
			if not ignore_errors:
				raise Exception("You misspelled a parameter, have a bad API key or require (new) OAuth (try reset_oauth?) ")
			else:
				logger.warn('401 error!')
				return {}
		else:
			raise Exception("incorrect status code! {response.status_code} : {response.reason}".format(**locals()))
	except (ConnectTimeout, ConnectionError):
		if retries > 0:
			return get(url, params, data, retries-1, timeout)
		else:
			logger.warning('retries for {url} exceeded (params={params}, data={data})'.format(**locals()))
			return {}


def search(q, maxpages=-1, expand=False, **kwargs):
	'''Searches for videos by using queries. 

	Parameters
	---
	q        : string
		terms to search
	maxpages : int(default=-1)
		maximum pages to retrieve, -1 for infinite
	expand   : bool(default=False)
		whether to expand hits
		**currently only works for videos!**
	
	kwargs: Please refer to https://developers.google.com/apis-explorer/#search/search/m/youtube/v3/youtube.search.list'
	for more information on possible criteria (passed as additional named arguments to the API)

	Yields
	---
	dict per retrieved resource
	
	'''
	url = "https://www.googleapis.com/youtube/v3/search"
	data = {
	'key':API_KEY,
	'type':'video',
	'part':'snippet',
	'maxResults':50,
	'q':q
	}
	data.update(**kwargs)
	res = get(url, params=data)
	if expand: 
		res['items'] = expand_videos(res['items'])
	for item in res.get('items',[]):
		yield item
	maxpages -= 1
	while maxpages!=0 and res.get('nextPageToken',0):
		maxpages -= 1
		item['PAGE'] = data.get('nextPageToken','')
		data.update({'pageToken':res['nextPageToken']})
		logger.info('searchpage = %s' %res['nextPageToken'])
		item['RETRIEVED_AT'] = now()
		res = get(url, params=data)
		if expand:
			res['items'] = expand_videos(res['items'])
		for item in res.get('items',[]):
			yield item

def expand_videos(vids, **kwargs ):
	videos = {vid.get('id',False):vid for vid in video_information(vids,**kwargs)}
	for vid in vids:
		vid.update(videos[vid['id']['videoId']])
	return vids

def video_information(videos, parts="all", **kwargs):
	'''
	Retrieves information (not comments) about a list of videos. 

	Parameters
	---
	videos: list
		The 'items' part of a video-search or a list of videoId's 
	
	parts: string(default='all')
		The properties to retieve per video, some may require OAuth,
		for example 'suggestions'. 
	kwargs:
		keyword-arguments passed as parameters to the API, see the
		documentation for details ( https://developers.google.com/youtube/v3/docs/videos )
	'''
	if not videos: yield 

	all_parts = {
	    'contentDetails': 2,
	    #'fileDetails': 1,
	    'id': 0,
	    #'liveStreamingDetails': 2,
	    #'localizations': 2,
	    #'player': 0,
	    #'processingDetails': 1,
	    #'recordingDetails': 2,
	    'snippet': 2,
	    'statistics': 2,
	    #'status': 2,
	    #'suggestions': 1,
	    'topicDetails': 2,
	}

	if parts=="all":
		parts = all_parts.keys()
	if type(parts)!=str:
		parts = ','.join(parts)

	if type(videos)==list and videos and type(videos[0])==dict:
		ids = ','.join([vid.get('id',{}).get('videoId') for vid in videos])
	elif type(videos)==list and videos and type(videos[0])==str:
		ids = ','.join(videos)
	elif type(videos)==str:
		ids = videos
	else:
		raise Exception("Unknown videos type!")

	data = {
	'key':API_KEY,
	'part':parts,
	'id':','.join([vid.get('id',{}).get('videoId') for vid in videos])
	}
	data.update(**kwargs)
	res = get('https://www.googleapis.com/youtube/v3/videos', params=data)
	for vid in res.get('items',[]):
		yield vid

def get_captions(vids, part="id, snippet", language='en', *args, **kwargs):
	if type(vids)==str:
		vids = [{'id':vids}]
	elif type(vids)==dict:
		vids = [vids]
	
	url = 'https://www.googleapis.com/youtube/v3/captions'

	data = {
	'key' : API_KEY,
	'part': part
	}

	for vid in vids:
		if vid.get('contentDetails',{}).get('caption','true')=='true':
			data.update({'videoId':vid['id']})
			captions = get(url, params=data).get('items',[])
		else:
			captions = [] # if captions are known not to exist, skip them
		vid['captions'] = captions['items']
		vid['caption']  = get_caption(vid,language=language)
		
	return vids

def get_caption(vid, language, types=['standard','ASR'], *args, **kwargs):
	caption_url = 'https://www.googleapis.com/youtube/v3/captions/'
	data = {'tfmt':'srt'}
	if vid.get('captions'):
		has_caps = {num:[cap for cap in vid['captions'] if 
				cap.get('snippet',{}).get('language','')==language and
				cap.get('snippet',{}).get('trackKind','')==captype
				] 
				for num, captype in enumerate(types)}
		best_choice = min(list(has_caps.keys())+[10])
		if best_choice < 10 :
			cap = get(caption_url+has_caps[best_choice][0]['id'], params=data, oauth=True)
			return {types[best_choice]:cap}
					
	else:
		return {'none':""}

def get_comments(video, for_type='video', maxpages=-1):
	parts = 'snippet'

	url = 'https://www.googleapis.com/youtube/v3/commentThreads' # appropriate comments endpoint

	# Allow for 'video' object to be either dicts or strings
	if type(video)==dict:
		rid = video.get('id')
	elif type(video)==str:
		rid = video
	else:
		raise Exception("unknown video argument type, should be a dict with an id key, or a sring!")

	# the data will be used as the parameters of the request
	data = {
	'key'       : API_KEY, # For authentication purposes
	'part'      : parts,
	'maxResults': 100 # Assume we want the maximum results possible
	}
	
	# pass the right parameter for videos, channels or channels+videos (allThreadsRelatedToChannel)
	if for_type=='video':
		data.update({'videoId':rid})
	elif for_type=='channel':
		data.update({'channelId':rid})
	elif for_type=='channel+videos':
		data.update({'allThreadsRelatedToChannelId':video})
	else:
		raise Exception("for_type should be 'video', 'channel' or 'channel+video'!")

	res  = get(url, params=data)
	for item in res.get('items',[]):
		yield item
	while  maxpages!=0 and res.get('nextPageToken',False):
		maxpages -= 1
		data.update({'pageToken':res.get('nextPageToken',False) or None})
		res = get(url, params=data)
		for item in res.get('items',[]): 
			yield item


