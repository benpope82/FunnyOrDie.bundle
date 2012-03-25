import re

TITLE = 'Funny or Die'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

URL_BASE = 'http://www.funnyordie.com'
URL_PATTERN = 'http://www.funnyordie.com/browse/videos/%s/all/%s/%s/%s'

CATEGORY_LIST = [
    { 'title': 'All', 'key': 'all' },
    { 'title': 'Stand Up', 'key': 'stand_up' },
    { 'title': 'Animation', 'key': 'animation' },
    { 'title': 'Web Series', 'key': 'web_series' },
    { 'title': 'Not Safe For Work', 'key': 'nsfw' },
    { 'title': 'Sketch', 'key': 'sketch' },
    { 'title': 'Sports', 'key': 'sports' },
    { 'title': 'Clean Comedy', 'key': 'clean_comedy' },
    { 'title': 'Politics', 'key': 'politics' },
    { 'title': 'Music', 'key': 'music' },
    { 'title': 'Parody', 'key': 'parody' },
    { 'title': 'Real Life', 'key': 'real_life' },
]

SORTS = [
    {
        'title': 'Most Buzz',
        'key': 'most_buzz',
        'allow_date_filter': True
    },
    {
        'title': 'Most Recent',
        'key': 'most_recent',
        'allow_date_filter': False
    },
    {
        'title': 'Most Viewed',
        'key': 'most_viewed',
        'allow_date_filter': True
    },
    {
        'title': 'Most Favorited',
        'key': 'most_favorited',
        'allow_date_filter': True
    },
    {
        'title': 'Highest Rated',
        'key': 'highest_rated',
        'allow_date_filter': True
    },
]

DATE_FILTERS = [
    {
        'title': 'Today',
        'key': 'today'
    },
    {
        'title': 'This Week',
        'key': 'this_week'
    },
    {
        'title': 'This Month',
        'key': 'this_month'
    },
    {
        'title': 'All Time',
        'key': 'all_time'
    },
]

####################################################################################################

def Start():
    Plugin.AddPrefixHandler('/video/funnyordie', Menu, TITLE, ICON, ART)
    Plugin.AddViewGroup("InfoList", viewMode = "InfoList", mediaType = "items")
    Plugin.AddViewGroup("List", viewMode = "List", mediaType = "items")

    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)
    ObjectContainer.view_group = 'List'

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    VideoClipObject.thumb = R(ICON)

####################################################################################################

def Menu():

    oc = ObjectContainer()
    for category in CATEGORY_LIST:
        oc.add(DirectoryObject(
            key = Callback(CategoryOptions, title = category['title'], category = category['key']), 
            title = category['title']))

    return oc

####################################################################################################

def CategoryOptions(title, category):
    oc = ObjectContainer(title2 = title)

    for sort in SORTS:
        if sort['allow_date_filter']:
            oc.add(DirectoryObject(
                key = Callback(
                  DateOptions, 
                  title = sort['title'], 
                  category = category, 
                  sort = sort['key']), 
                title = sort['title']))
        else:
            oc.add(DirectoryObject(
                key = Callback(
                    VideoList, 
                    title = sort['title'], 
                    category = category, 
                    sort = sort['key'],
                    date = 'all_time'), 
                title = sort['title']))            
    return oc

####################################################################################################

def DateOptions(title, category, sort):
    oc = ObjectContainer(title2 = title)

    for date_filter in DATE_FILTERS:
        oc.add(DirectoryObject(
            key = Callback(
                VideoList, 
                title = date_filter['title'], 
                category = category, 
                sort = sort,
                date = date_filter['key']), 
            title = date_filter['title']))  
    return oc

####################################################################################################

def VideoList(title, category, sort, date, page = 1):
    oc = ObjectContainer(title2 = "%s: %s" % (title, str(page)), view_group = "InfoList")

    videos = HTML.ElementFromURL(URL_PATTERN % (category, sort, date, page))
    for video in videos.xpath('//div[@class="detailed_vp"]'):

        url = URL_BASE + video.xpath('.//a')[0].get('href')
        title = video.xpath('.//a[@class = "title"]/text()')[0]
        thumb = video.xpath('.//img[@class = "thumbnail"]')[0].get('src')

        duration_text = video.xpath('.//span[@class = "duration"]/text()')[0]
        duration_dict = re.match("(?P<mins>[0-9]+):(?P<secs>[0-9]+)", duration_text).groupdict()
        mins = int(duration_dict['mins'])
        secs = int(duration_dict['secs'])
        duration = ((mins * 60) + secs) * 1000

        oc.add(VideoClipObject(
            url = url,
            title = title,
            thumb = Callback(GetThumb, url = thumb),
            duration = duration))

    oc.add(DirectoryObject(
        key = Callback(
            VideoList, 
            title = title, 
            category = category, 
            sort = sort,
            date = date,
            page = page + 1), 
        title = "Next Page..."))  

    return oc

####################################################################################################

def GetThumb(url):
    try:
        data = HTTP.Request(url.replace('medium', 'large')).content
        return DataObject(data, 'image/png')
    except: pass
        
    try:
        data = HTTP.Request(url).content
        return DataObject(data, 'image/png')
    except: pass

    return Redirect(R(ICON))