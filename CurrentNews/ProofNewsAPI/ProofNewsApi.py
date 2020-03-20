import requests
import config
from copy import copy
from HTMLParser import HTMLParser


class ProofNewsApi(object):
    def __init__(self, _ep = config.PROOF_NEWS_API):
        self.RSSFeedSoup = []
        self.endpoint = _ep


    def getRequestAndReturnRequestJSON(self,_endpoint):
        resp = requests.get(_endpoint)
        return resp.json()


    def returnProcessedJSON(self, _json_obj):
        RANGE = 3
        article_list = copy(_json_obj.get("data"))
        print "JAPI _ LIST === %s" % article_list

        if len(article_list) > 2:
            for x in range(0,RANGE - 1):
                article_list[x]["headline"] = "| NEW | %s" % article_list[x]["headline"]

        return article_list


    def processDict(self, _dict):

        return_dict = {
            "title" : HTMLParser().unescape(_dict.get("headline")) if _dict.get("headline") else None,
            "url"  : _dict.get("url")
        }

        return return_dict


    def run(self):
        json_obj = self.getRequestAndReturnRequestJSON(self.endpoint)
        return_dicts = self.returnProcessedJSON(json_obj)
        return_dicts = [self.processDict(d) for d in return_dicts]
        return return_dicts
