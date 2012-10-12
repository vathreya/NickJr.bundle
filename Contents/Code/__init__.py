NAMESPACES = {'media':'http://search.yahoo.com/mrss/'}

NICK_ROOT = 'http://www.nickjr.com'
NICK_SHOWS_LIST = 'http://www.nickjr.com/common/data/kids/get-kids-config-data.jhtml?fsd=/dynaboss&urlAlias=kids-video-landing&af=false'
RSS_FEED = 'http://www.nickjr.com/dynamo/video/data/mrssGen.jhtml?type=network&loc=default&hub=kids&mode=playlist&dartSite=nickjr.playtime.nol&mgid=mgid:cms:item:nickjr.com:%s&demo=null&block=true'

NAME = 'Nick Jr.'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

RE_CMSID = Regex('KIDS\.add\("cmsId", "(\d+)"\)')

####################################################################################################
def Start():

	Plugin.AddPrefixHandler('/video/nickjr', MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

	ObjectContainer.title1 = NAME
	ObjectContainer.view_group = 'InfoList'
	ObjectContainer.art = R(ART)

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:15.0) Gecko/20100101 Firefox/15.0.1'

####################################################################################################
def MainMenu():

	oc = ObjectContainer()
	content = JSON.ObjectFromURL(NICK_SHOWS_LIST)

	for item in content['config']['promos'][0]['items']:
		title = item['title'].replace('&amp;', '&')

		if title == 'Featured Nick Jr. Videos':
			continue

		thumb = NICK_ROOT + item['thumbnail']
		url = NICK_ROOT + item['link']

		oc.add(DirectoryObject(key=Callback(ShowList, title=title, thumb=thumb, url=url), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=R(ICON))))

	return oc

####################################################################################################
def ShowList(title, thumb, url):

	oc = ObjectContainer(title2=title)

	show_page = HTTP.Request(url).content
	cmsid = RE_CMSID.search(show_page).group(1)
	feed = XML.ElementFromURL(RSS_FEED % cmsid)

	for item in feed.xpath('//item'):

		title = item.xpath('.//media:title', namespaces=NAMESPACES)[0].text
		summary = item.xpath('.//media:description', namespaces=NAMESPACES)[0].text
		url = item.xpath('.//media:player', namespaces=NAMESPACES)[0].get('url')

		thumb = item.xpath('.//media:thumbnail', namespaces=NAMESPACES)[0].get('url')

		if 'dynaboss' not in thumb:
			thumb = thumb.replace('assets', 'dynaboss/assets')

		try:
			duration = int(item.xpath('.//media:content', namespaces=NAMESPACES)[0].get('duration')) * 1000
		except:
			duration = None

		oc.add(VideoClipObject(
			url = url,
			title = title,
			summary = summary,
			duration = duration,
			thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=R(ICON))
		))

	return oc
