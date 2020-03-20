import requests
import json
from BeautifulSoup import BeautifulSoup as BS
import config
import re
from random import choice
"""
limit, offset, search by title, topic
"""

class GoogleNewsRequester(object):
    def __init__(self, _subject = "blockchain", _num_pages = 5, _raw = False):
        self.query_asc_endpoint = config.GOOG_FRAME_QUERY_ASC if _raw == False else config.GOOG_FRAME_RAW_QUERY_ASC #{query} AND {start}
        self.current_page = 0
        self.increment = 10
        self.cur_subject = _subject
        self.category = "news"
        self.num_pages = _num_pages
        self.filter_regex = "q=(.*)&"

    def makeRequestAndReturnHTML(self):
        this_header = {"User-Agent" : choice(config.USERAGENT_LIST)}
        resp = requests.get(self.query_asc_endpoint.format(query = self.cur_subject, start = self.current_page), proxies = config.PROXY_DICT)
        return resp.content

    def filterUrl(self,_goog_url):
        rex = re.compile(self.filter_regex)
        try:
            return rex.findall(_goog_url)[0].split("&")[0]
        except:
            return _goog_url

    def parseArticleSoup(self,_article_soup):
        """

            received_to_target_structure = {
                "title" : "title",
                "when" : "publishedAt",
                "url" : "url",
                "img" : "urlToImage",
                "type" : "",
                "description" : "description"
            }
        """
        try:
            article_struct = {}
            article_struct["title"] = _article_soup.find("h3",{"class" : "r"}).text
            article_struct["url"] = self.filterUrl(_article_soup.find("h3",{"class" : "r"}).find("a")["href"])
            article_struct["img"] = _article_soup.find("img",{"class":"th"})["src"]

            sub_labels = _article_soup.find("div",{"class" : "slp"}).find("span").text.split(" - ")
            article_struct["type"] = sub_labels[0]
            article_struct["when"] = sub_labels[1]
            article_struct["description"] = _article_soup.find("div",{"class": "st"}).getText(" ")
            article_struct["category"] = self.category

            return article_struct
        except:
            return None


    def scrapePageAndReturnFormattedDictionaries(self,_html):

        """
            @returns [received_to_target_structure, received_to_target_structure, '...']
        """

        soup = BS(_html)
        raw_articles = soup.findAll("div",{"class" : "g"})
        article_list = [self.parseArticleSoup(_art) for _art in raw_articles]

        return article_list

    def getArtList(self):
        article_list = []

        for i in range(self.num_pages):
            html_string = self.makeRequestAndReturnHTML()
            cur_art_list = self.scrapePageAndReturnFormattedDictionaries(html_string)
            article_list.extend(cur_art_list)
            self.current_page += self.increment

        return article_list




def test():
    G = GoogleNewsRequester("ethereum",5)
    print G.getArtList()
