SHOW_LIST = 'http://www.nick.com/apps/api/v2/editorial-content-categories/properties?apiKey=comgcgbf&killDBSequenceNumber='
SHOW_VIDEO = 'http://www.nick.com/apps/api/v2/content-collection?apiKey=comgcgbf&killDBSequenceNumber=&orderBy=MinDpStartDateDesc&rows=36&series=%s&start=0&types=video%%2Cepisode'

####################################################################################################
def Start():

	ObjectContainer.title1 = 'Nick Jr.'
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
	HTTP.Headers['Cookie'] = 'Visited=Yes'

####################################################################################################
@handler('/video/nickjr', 'Nick Jr.')
def MainMenu():

	oc = ObjectContainer()
	json_obj = JSON.ObjectFromURL(SHOW_LIST)

	for show in json_obj:

		if 'seriesTitle' not in show:
			continue

		id = show['urlKey']
		title = show['seriesTitle']
		thumb = 'http://www.nickjr.com%s' % (show['images'][0]['assets'][0]['path'])

		oc.add(DirectoryObject(
			key = Callback(Episodes, id=id, title=title),
			title = title,
			thumb = Resource.ContentsOfURLWithFallback(url=thumb)
		))

	return oc

####################################################################################################
@route('/video/nickjr/episodes')
def Episodes(id, title):

	oc = ObjectContainer(title2=title)
	json_obj = JSON.ObjectFromURL(SHOW_VIDEO % (id))

	for video in json_obj['results']:

		if 'authRequired' in video and video['authRequired']:
			continue

		id = video['id']
		title = video['shortTitle']

		if video['type'] == 'episode':
			title = '%s (Full Episode)' % (title)

		summary = video['description']
		thumb = 'http://www.nickjr.com%s' % (video['images'][0]['assets'][0]['path'])
		duration = Datetime.MillisecondsFromString(video['duration'])
		originally_available_at = Datetime.ParseDate(video['datePosted'].split('T')[0]).date()

		oc.add(VideoClipObject(
			url = 'nickjr://%s' % (id),
			title = title,
			summary = summary,
			thumb = Resource.ContentsOfURLWithFallback(url=thumb),
			duration = duration,
			originally_available_at = originally_available_at
		))

	return oc
