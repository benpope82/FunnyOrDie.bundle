TITLE = 'Funny or Die'

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

    ObjectContainer.title1 = TITLE

####################################################################################################
@handler('/video/funnyordie', 'Funny or Die')
def MainMenu():

    oc = ObjectContainer()

    for category in CATEGORY_LIST:

        oc.add(DirectoryObject(
            key = Callback(CategoryOptions, title = category['title'], category = category['key']),
            title = category['title']
        ))

    oc.add(SearchDirectoryObject(identifier='com.plexapp.plugins.funnyordie', title='Search', prompt='Search for Videos'))

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
                    sort = sort['key']
                ),
                title = sort['title']
            ))
        else:
            oc.add(DirectoryObject(
                key = Callback(
                    VideoList,
                    title = sort['title'],
                    category = category,
                    sort = sort['key'],
                    date = 'all_time'
                ),
                title = sort['title']
            ))

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
                date = date_filter['key']
            ),
            title = date_filter['title']
        ))

    return oc

####################################################################################################
def VideoList(title, category, sort, date, page = 1):

    oc = ObjectContainer(title2 = "%s: %s" % (title, str(page)))
    videos = HTML.ElementFromURL(URL_PATTERN % (category, sort, date, page))

    for video in videos.xpath('//article[contains(@class, "video-preview")]'):

        # Filter out any videos which are not hosted, but are instead 'embedded'. I've only found
        # one example of this, but didn't actually play online
        url = URL_BASE + video.xpath('./a/@href')[0]
        if url.startswith('http://www.funnyordie.com/videos/') == False:
            continue

        title = video.xpath('./a/@title')[0]
        thumb = video.xpath('./a/img/@src')[0]

        oc.add(VideoClipObject(
            url = url,
            title = title,
            thumb = Resource.ContentsOfURLWithFallback(url=thumb)
        ))

    oc.add(NextPageObject(
        key = Callback(
            VideoList,
            title = title,
            category = category,
            sort = sort,
            date = date,
            page = page + 1
        ),
        title = "Next Page..."
    ))

    return oc
