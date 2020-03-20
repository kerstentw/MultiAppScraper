import config
import threading
import requests
from BeautifulSoup import BeautifulSoup as BS
import re
from random import shuffle
from HTMLParser import HTMLParser


class RSSFeedReader(object):
    def __init__(self):
        self.RSSFeedSoup = []

    def getTRequestAndReturnRequestObject(self,_endpoint):
        resp = requests.get(_endpoint)
        soup = BS(resp.content).findAll("item")
        self.RSSFeedSoup.extend(soup)


    def cleanString(self,_uri_text):
        return re.sub(r"&#[0-9]{0,5};","",_uri_text)


    def turnSoupIntoDict(self, _soup):
        title = _soup.find("title")
        link = _soup.find("guid")

        return_dict = {
            "title" : HTMLParser().unescape(title.text) if title else None,
            "url"  : link.text if link else None,
        }

        return return_dict



    def run(self):
        threadList = []
        for _ep in config.FEED_LIST:
            print _ep
            Thread = threading.Thread(target=self.getTRequestAndReturnRequestObject, args = (_ep,))
            t = Thread.start()
            threadList.append(Thread)

        for _t in threadList:
            _t.join()

        return_dicts = []

        for _soup in self.RSSFeedSoup:
            return_dicts.append(self.turnSoupIntoDict(_soup))
        shuffle(return_dicts)

        return return_dicts
