NICK_ROOT = 'http://www.nickjr.com'
NICK_SHOWS_LIST = 'http://www.nickjr.com/common/data/kids/get-kids-config-data.jhtml?urlAlias=kids-video-landing'
RSS_FEED = 'http://www.nickjr.com/dynamo/video/data/mrssGen.jhtml?type=network&loc=default&hub=kids&mode=playlist&dartSite=nickjr.playtime.nol&mgid=mgid:cms:item:nickjr.com:%s&demo=null&block=true'

NAMESPACES = {'media':'http://search.yahoo.com/mrss/'}

RE_CMSID = Regex('KIDS\.add\("cmsId", "(\d+)"\)')

####################################################################################################
def Start():

	ObjectContainer.title1 = 'Nick Jr.'
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.94 Safari/537.36'

####################################################################################################
@handler('/video/nickjr', 'Nick Jr.')
def MainMenu():

	oc = ObjectContainer()
	content = JSON.ObjectFromURL(NICK_SHOWS_LIST)

	for item in content['config']['promos'][0]['items']:

		title = item['title'].replace('&amp;', '&')

		if title.lower() in ('featured nick jr. videos'):
			continue

		thumb = NICK_ROOT + item['thumbnail']
		url = NICK_ROOT + item['link']

		oc.add(DirectoryObject(
			key = Callback(ShowList, title=title, url=url),
			title = title,
			thumb = Resource.ContentsOfURLWithFallback(url=thumb)
		))

	return oc

####################################################################################################
@route('/video/nickjr/show')
def ShowList(title, url):

	oc = ObjectContainer(title2=title)

	show_page = HTTP.Request(url).content
	cmsid = RE_CMSID.search(show_page).group(1)
	feed = XML.ElementFromURL(RSS_FEED % cmsid)

	for item in feed.xpath('//item'):

		url = item.xpath('.//media:player/@url', namespaces=NAMESPACES)[0]
		title = item.xpath('.//media:title/text()', namespaces=NAMESPACES)[0]
		summary = item.xpath('.//media:description/text()', namespaces=NAMESPACES)[0]
		thumb = item.xpath('.//media:thumbnail/@url', namespaces=NAMESPACES)[0]

		if '/dynaboss/' in thumb:
			thumb = thumb.replace('/dynaboss/', '/')

		try:
			duration = int(item.xpath('.//media:content/@duration', namespaces=NAMESPACES)[0]) * 1000
		except:
			duration = None

		oc.add(VideoClipObject(
			url = url,
			title = title,
			summary = summary,
			duration = duration,
			thumb = Resource.ContentsOfURLWithFallback(url=thumb)
		))

	return oc
