import re

NAMESPACES = {'media':'http://search.yahoo.com/mrss/'}

NICK_ROOT = "http://www.nickjr.com"
NICK_SHOWS_LIST = "http://www.nickjr.com/common/data/kids/get-kids-config-data.jhtml?fsd=/dynaboss&urlAlias=kids-video-landing&af=false"
RSS_FEED = "http://www.nickjr.com/dynamo/video/data/mrssGen.jhtml?type=network&loc=default&hub=kids&mode=playlist&dartSite=nickjr.playtime.nol&mgid=mgid:cms:item:nickjr.com:%s&demo=null&block=true"

NAME = 'Nick Jr.'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

####################################################################################################
def Start():

	Plugin.AddPrefixHandler('/video/nickjr', MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

	MediaContainer.art = R(ART)
	MediaContainer.title1 = NAME
	MediaContainer.viewGroup = 'List'
	DirectoryItem.thumb = R(ICON)

	HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
def MainMenu():

	dir = MediaContainer()
	content = JSON.ObjectFromURL(NICK_SHOWS_LIST)

	for item in content['config']['promos'][0]['items']:
		title = item['title'].replace('&amp;', '&')

		if item['thumbnail'].endswith('.jpg'):
			image = NICK_ROOT + item['thumbnail']
		elif item['promoImage'].endswith('.jpg'):
			image = NICK_ROOT + item['promoImage']
		else:
			image = None

		link = NICK_ROOT + item['link']

		dir.Append(Function(DirectoryItem(ShowList, title, thumb=Function(GetThumb, url=image)), image = image, pageUrl = link))

	return dir

####################################################################################################
def ShowList(sender, image, pageUrl):

	dir = MediaContainer(title2=sender.itemTitle)
	full_episodes = []
	clips = []

	showcontent = HTTP.Request(pageUrl).content
	m = re.compile('KIDS.add."cmsId", ".+?".;').findall(showcontent)
	cmsid = m[0].split('"')[3]
	url = RSS_FEED % (cmsid)
	feedcontent = XML.ElementFromURL(url)

	for item in feedcontent.xpath('//item'):
		title = item.xpath('.//media:title', namespaces=NAMESPACES)[0].text
		link = item.xpath('.//media:player', namespaces=NAMESPACES)[0].get('url')

		thumb = item.xpath('.//media:thumbnail', namespaces=NAMESPACES)[0].get('url')

		if thumb.find('dynaboss') == -1:
			thumb = thumb.replace("assets", "dynaboss/assets")

		try:
			duration = int(item.xpath('.//media:content', namespaces=NAMESPACES)[0].get('duration').replace(':', '')) * 1000   ##ADDED replace(':', '') FOR PROTECTION AGAINST A FEW VIDEOS THAT HAVE "MIN:SEC" RATHER THAN JUST "SEC" 
		except:
			duration = "0"
		
		summary = item.xpath('.//media:description', namespaces=NAMESPACES)[0].text

		if item[0].xpath('..//media:category[@label="full"]', namespaces=NAMESPACES):
			full_episodes.append((title, thumb, summary, link, duration))
		elif item[0].xpath('..//media:category[@label="Playtime Clip"]', namespaces=NAMESPACES):
			clips.append((title, thumb, summary, link, duration))

	if len(full_episodes) > 0:
		dir.Append(Function(DirectoryItem(VideoList, title="Full Episodes", thumb=Function(GetThumb, url=image)), videolist=full_episodes))

	if len(clips) > 0:
		dir.Append(Function(DirectoryItem(VideoList, title="Clips", thumb=Function(GetThumb, url=image)), videolist=clips))

	return dir

####################################################################################################
def VideoList(sender, videolist):

	dir = MediaContainer(title2=sender.itemTitle, viewGroup='InfoList')

	for vid in videolist:
		dir.Append(WebVideoItem(url=vid[3], title=vid[0], thumb=Function(GetThumb, url=vid[1]), summary=vid[2], duration=vid[4]))

	return dir

####################################################################################################
def GetThumb(url):

	if url:
		try:
			image = HTTP.Request(url, cacheTime=CACHE_1WEEK).content
			return DataObject(image, 'image/jpeg')
		except:
			pass

	return Redirect(R(ICON))
