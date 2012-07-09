NAMESPACES = {'media':'http://search.yahoo.com/mrss/'}

NICK_ROOT = "http://www.nickjr.com"
NICK_SHOWS_LIST = "http://www.nickjr.com/common/data/kids/get-kids-config-data.jhtml?fsd=/dynaboss&urlAlias=kids-video-landing&af=false"
RSS_FEED = "http://www.nickjr.com/dynamo/video/data/mrssGen.jhtml?type=network&loc=default&hub=kids&mode=playlist&dartSite=nickjr.playtime.nol&mgid=mgid:cms:item:nickjr.com:%s&demo=null&block=true"

NAME = L('Title')
ART = 'art-default.jpg'
ICON = 'icon-default.png'

REGEX = Regex('KIDS.add."cmsId", ".+?".;')

####################################################################################################
def Start():

	Plugin.AddPrefixHandler('/video/nickjr', MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

	ObjectContainer.title1 = NAME
	ObjectContainer.view_group = 'List'
	ObjectContainer.art = R(ART)
	
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:13.0) Gecko/20100101 Firefox/13.0.1'

####################################################################################################
def MainMenu():

	oc = ObjectContainer()
	
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

		oc.add(DirectoryObject(key = Callback(ShowList, image=image, pageUrl=link), title=title, thumb=Resource.ContentsOfURLWithFallback(url=image, fallback=R(ICON))))

	return oc

####################################################################################################
def ShowList(image, pageUrl):

	oc = ObjectContainer()
	
	full_episodes = []
	clips = []
	
	showcontent = HTTP.Request(pageUrl).content
	m = REGEX.findall(showcontent)
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
			duration = 0
		
		summary = item.xpath('.//media:description', namespaces=NAMESPACES)[0].text

		if item[0].xpath('..//media:category[@label="full"]', namespaces=NAMESPACES):
			clips.append((title, thumb, summary, link, duration))
		elif item[0].xpath('..//media:category[@label="Playtime Clip"]', namespaces=NAMESPACES):
			clips.append((title, thumb, summary, link, duration))
		elif item[0].xpath('..//media:category[@label="NickJr Clip"]', namespaces=NAMESPACES):
			clips.append((title, thumb, summary, link, duration))
		
	if len(clips) > 0:
		for vid in clips:
			title=vid[0]
			thumb=vid[1]
			summary=vid[2]
			url=vid[3]
			duration=vid[4]
			
			oc.add(VideoClipObject(
				url = url,
				title = title,
				summary = summary,
				duration = duration,
				thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=R(ICON)),
			))
			
	return oc
