from BeautifulSoup import BeautifulSoup as BS
import config
import requests
import json
import re
import time
from datetime import datetime
from HTMLParser import HTMLParser

#TODO Build Grabber Base Class with Requester as Parent

class NewsGrabber(object):
    def __init__(self):
        self.timeFile = "newsapi_timefile.txt"
        self.picklefile = "current_news"

    def writeTimeFile(self, _time):
        with open(self.timeFile) as my_fil:
            my_fil.write(_time)

    def getFromNewsApi(self, _query):

        endpoint = config.NEWSAPI_GOOG_FRAME.format(search_term = _query)
        print endpoint
        resp = requests.get(endpoint)
        return resp.content




class RedditGrabber(object):
    _headers = {"authority":"old.reddit.com","user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36","upgrade-insecure-requests":"1"}
    def __init__(self,_endpoint = "cryptocurrency"):
        self.host = "https://old.reddit.com/r/"
        self.resp = requests.get(self.host + _endpoint, headers = self._headers)

        if self.resp.ok != True:
            self.resp = requests.get("https://old.reddit.com/r/cryptocurrency", headers = self.headers)

        self.soup = BS(self.resp.content)
        self.postList = []
        self.post = {}

    def computeQualityRating(self):
        pass

    def getParentContainer(self):
        return self.soup.find("div",{"class":"linklisting"})

    def getPostElements(self):
        _parent_container = self.soup.find("div",{"id":"siteTable"})
        return _parent_container.findAll("div",{"data-type":"link"})


    def placePostData(self, _main_element):
        base_host = "http://www.reddit.com"

        self.post["karma-ranking"] = _main_element.get("data-score")
        self.post["comment_count"] = _main_element.get("data-comments-count")
        self.post["subreddit"] = _main_element.get("data-subreddit")
        self.post["author"] = _main_element.get("data-author-fullname")
        self.post["timestamp"] = int(_main_element.get("data-timestamp"))
        self.post["link-type"] = _main_element.get("data-type")
        self.post["comment-link"] = base_host + _main_element.get("data-permalink")
        self.post["content-link"] = _main_element.get("data-url")

        self.post["img"] = "http:"+_main_element.find("img").get("src") if _main_element.find("img") else None
        self.post["title"] = _main_element.find("a",{"data-event-action":"title"}).text

        return True


    def buildPostStruct(self,_main_element):
        self.post = {}
        self.placePostData(_main_element)
        self.postList.append(self.post)


    def getRedditPosts(self):
        post_list = self.getPostElements()
        for _post in post_list:
            self.buildPostStruct(_post)

        return self.postList


class RedditSearcher(object):
    _headers = {"authority":"old.reddit.com","user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36","upgrade-insecure-requests":"1"}
    def __init__(self,_endpoint = "cryptocurrency"):
        self.host = "https://old.reddit.com/r/"
        self.host = "https://www.reddit.com/search/.json?t=day&sort=top&q="
        self.resp = requests.get(self.host + _endpoint, headers = self._headers)

        if self.resp.ok != True:
            self.resp = requests.get("https://www.reddit.com/search/.json?q=cryptocurrency", headers = self.headers)

        self.resp = self.resp.json()
        self.postList = []
        self.post = {}

    def computeQualityRating(self):
        pass

    def getParentContainer(self):
        return self.soup.find("div",{"class":"linklisting"})

    def getPostElements(self):
        _parent_container = self.resp.get("data")
        return _parent_container.get("children") if _parent_container else []


    def placePostData(self, _main_element):
        base_host = "http://www.reddit.com"

        self.post["karma-ranking"] = _main_element.get("score")
        self.post["comment_count"] = _main_element.get("num_comments")
        self.post["subreddit"] = _main_element.get("subreddit_name_prefixed")
        self.post["author"] = _main_element.get("author")
        self.post["timestamp"] = int(_main_element.get("created")) * 1000
        self.post["link-type"] = _main_element.get("post_hint")
        self.post["comment-link"] = base_host + _main_element.get("permalink")
        self.post["content-link"] = _main_element.get("url")

        self.post["img"] = _main_element.get("thumbnail") if _main_element.get("thumbnail") != self and len(_main_element.get("thumbnail")) > 0 else None
        self.post["title"] = _main_element.get("title")

        return True


    def buildPostStruct(self,_main_element):
        self.post = {}
        self.placePostData(_main_element)
        self.postList.append(self.post)


    def getRedditPosts(self):
        post_list = self.getPostElements()
        for _post in post_list:
            self.buildPostStruct(_post.get("data"))

        return self.postList


class BTCTalkGrabber(object):
    def __init__(self):
        self.bitcoinForumURL = "https://bitcointalk.org/index.php?board=1"
        self.altcoinForumURL=  "https://bitcointalk.org/index.php?board=67.0"

    def returnForumBoard(self,url):
        response = requests.get(url, proxies = config.PROXY_DICT)
        print response.content
        htmlContent = response.content
        beautifulSoupHTML = BS(htmlContent)
        beautifulSoupBody = beautifulSoupHTML.body
        board = beautifulSoupBody.findAll("div",{"class":"tborder"})
        print board
        return board


    def return_collapse_boardList(self):
        bitcoinForumBoardList = self.makeBitCoinForumBoardList()
        altcoinForumBoardList = self.makeAltCoinForumBoardList()

        collapseBoardList = []
        collapseBoardList.extend(bitcoinForumBoardList)
        collapseBoardList.extend(altcoinForumBoardList)

        collapseBoardList_orderby_timestamp=sorted(collapseBoardList, key=lambda post: int(post['lastPost']['date']))
        collapseBoardList_orderby_timestamp.reverse()

        return collapseBoardList_orderby_timestamp

    def makeAltCoinForumBoardList(self):
        altcoinForumBoardList = []
        board = self.returnForumBoard(self.altcoinForumURL)
        posts = board[1].findAll("tr")
        altcoinForumBoardList = self.organize_postsList_to_dict(posts,"altcoin")
        return altcoinForumBoardList


    def makeBitCoinForumBoardList(self):
        bitcoinForumBoardList = []
        board = self.returnForumBoard(self.bitcoinForumURL)
        posts = board[2].findAll("tr")
        bitcoinForumBoardList = self.organize_postsList_to_dict(posts,"bitcoin")
        return bitcoinForumBoardList


    def organize_postsList_to_dict(self, posts, _board_type = "altcoin"):
        boardList = []
        sticky_rex = re.compile("stickyicon(.*)")

        for i in range(1,len(posts)):

            if posts[i].find("img",{"id":sticky_rex}):
                continue

            tempdic = {
            "board" : _board_type,
            "title" : posts[i].findAll("td")[2].a.text.strip(),
            "url" : posts[i].findAll("td")[2].a['href'],
            "user" : posts[i].findAll("td")[3].text.strip(),
            #"user_url" : posts[i].findAll("td")[3].a['href'],
            "replies" : posts[i].findAll("td")[4].text.strip(),
            "views" : posts[i].findAll("td")[5].text.strip(),
            "lastPost" : {
                           "date" : self.convertToTimestamp(posts[i].findAll("td")[6].span.text.split("by")[0].strip()),
                           "user" : posts[i].findAll("td")[6].span.a.text
                         }
                    }
            boardList.append(tempdic)
        return boardList


    def convertToTimestamp(self,_timestring):
        '''
        Converts 'Today at 04:46:59 AM' OR 'April 24, 2018, 07:41:24 AM' to:
        'Thu May 31 04:46:59 AM'
        "%a %b %d %I:%M:%S %p"
        '''

        now = [t for t in time.ctime().split(" ") if len(t) > 0]
        btc_talk_struct = _timestring.split(" ")


        if "Today" in btc_talk_struct[0]:
            time_format = "%b %d, %Y, %I:%M:%S %p"
            time_string_formatter ="{month} {day}, {year}, {time} {orientation}"

            hhmm_time = btc_talk_struct[-2]
            orientation = btc_talk_struct[-1]
            month = now[1]
            day = now[2]
            this_year = now[-1]

            ts = time_string_formatter.format(month = month, day = day, year = this_year, time = hhmm_time, orientation = orientation)

        else:
            time_format = "%B %d, %Y, %I:%M:%S %p"
            ts = _timestring


        return int(time.mktime(datetime.strptime(ts,time_format).timetuple())) * 1000


class CoinTelegraphGrabber(object):
    def __init__(self):
        pass


TextualScrapersDirectory = {
    "news_grabber" : NewsGrabber,
    "reddit_grabber" : RedditGrabber,
    "btc_talk_grabber" : BTCTalkGrabber,
    "coin_telegraph_grabber" : CoinTelegraphGrabber
}
