# -*- coding: utf-8 -*-

import json
import requests
import threading
from NewsAcquisitionInterface import NewsAcquisitionInterface
from BeautifulSoup import BeautifulSoup as BS
from TwitterInterface.TwitterInterface import TwitterInterface as TI
from TwitterInterface.TwitterInterface import TwitterScraper as TS
import time
from itertools import groupby
from collections import Counter
import traceback

class BasicSentimentInterface(object):
    def __init__(self):
        pass


class TwitterSearch(BasicSentimentInterface):
    def __init__(self):
        self.twitter_handler = TI()

    def rawSearch(self, _query):
        return self.twitter_handler.searchTwitter(_query)


class SingleTweet(BasicSentimentInterface):
    def __init__(self, username = "avocadobyproof"):
        self.twitter_handler = TS("https://mobile.twitter.com/" + username)

    def rawSearch(self):
        return self.twitter_handler.getFirstTwenty()

class NewsSentiment(BasicSentimentInterface):

    def __init__(self, _subject):
        SubjectObject = NewsAcquisitionInterface(_subject)
        IndustryObject = NewsAcquisitionInterface("blockchain")
        self.subject_list = SubjectObject.grabNewsAPIAndReturnAsDict()
        self.industry_list = IndustryObject.grabNewsAPIAndReturnAsDict()
        self.subject_raw = SubjectObject.returnRaw()
        self.industry_raw = IndustryObject.returnRaw()
        self.industry_url_list = [_holder["url"] for _holder in self.industry_list]
        self.subject = _subject
        self.mentions = 0
        self.thread_count = []
        self.article_list = []

    def most_common_words_by_asset(self):
        word_soup = " ".join([_holder_dict["description"] for _holder_dict in self.subject_list if _holder_dict["description"]])
        word_list = word_soup.split(" ")
        word_counts = Counter(word_list)
        helper_words = ["0","its","for","it's","what's","the","a","is","and","an", "if","you", "his", "her", "so", "but","1","2","3","4","5","6","7","8","9","from","over","via","be","put","on","of","were","was","or", "and",".","-","!",",","who","what","where","why","how"]

        return {word:word_counts[word] for word in word_counts if word.isalpha() and word.lower() not in helper_words and word_counts[word] > 1}

    def returnNumSubjectArticles(self):
        return self.subject_raw.get("totalResults")

    def returnNumIndustryArticles(self):
        return self.industry_raw.get("totalResults")

    def returnPopularityRatioMacro(self):
        sub = self.subject_raw.get("totalResults")
        ind = self.industry_raw.get("totalResults")

        if ind <= 0:
            return 0

        return float(sub) / float(ind)

    def returnPopularityRatio(self):
        sub_len = len(self.subject_list)
        ind_len = len(self.industry_list)

        return sub_len / float(ind_len)


    def countMentionsInIndustryNews(self, _endpoint):
        self.mentions = 0
        #print "GETTING::: %s" % _endpoint
        resp = requests.get(_endpoint)
        #print resp.status_code
        self.article_list.append(resp)
        #print "FINISHED"

    def threadOutCount(self):
        for _endpoint in self.industry_url_list:
            t = threading.Thread(target = self.countMentionsInIndustryNews, args = (_endpoint,))
            t.run()
            #self.thread_list.append(t)

        for _resp in self.article_list:
            target_text = BS(_resp.content).find("body").text
            self.mentions += target_text.count(self.subject)


    def runSuite(self):
        #threads = self.threadOutCount()

        sentiment = {
            "common_words" : self.most_common_words_by_asset(),
            "number_of_articles" : self.returnNumIndustryArticles(),
            "popularity_ratio" : self.returnPopularityRatioMacro(),
            "number_of_articles_with_mention" : self.returnNumSubjectArticles(),
            #"industry_links" : self.industry_list, #Turn on if usecase arises.  Otherwise, this just creates bloat.
            "subject_links" : self.subject_list
        }
        return sentiment



class NewsSentPage(object):
    TARGET_FILE = "news_sent_page.txt"
    TIME_FILE = "time_file.txt"
    returnPages = {}
    ONE_DAY = 86400

    def getTopTwenty(self,_limit=20):
        data = requests.get("https://api.coinmarketcap.com/v2/ticker/?start=101&limit={lim}&start=1&structure=array".format(lim=_limit)).json().get("data")[:_limit]

        subject_list = [_d["name"] for _d in data]
        print len(subject_list)
        return subject_list

    def returnPage(self, _subject):
        NS = NewsSentiment(_subject)
        self.returnPages[_subject] = NS.runSuite()

    def isMemoisedFileFresh(self):
        try:
            target_check = open(self.TARGET_FILE, "r").read()
            mem_time = open(self.TIME_FILE, "r").read()
            if len(mem_time) > 0 and mem_time.isdigit():
                mem_time = int(mem_time)
                if (time.time() - mem_time) >= self.ONE_DAY:
                    return False
                else:
                    return True

            return False
        except:
            traceback.print_exc()
            return False

    def createMemFile(self,_struct):
        try:
            with open(self.TARGET_FILE,"w") as t_file:
                t_file.write(str(_struct))
            with open(self.TIME_FILE,"w") as time_file:
                time_file.write(str(int(time.time())))
            return True
        except:
            return False

    def readMemFile(self):
        with open(self.TARGET_FILE,"r") as t_file:
            structure = eval(t_file.read())
        return structure

    def buildSentPage(self,_limit = 20):
        threads = []
        if self.isMemoisedFileFresh():
            return self.readMemFile()

        else:
            for _sub in self.getTopTwenty(_limit):
                 t = threading.Thread(target=self.returnPage, args=(_sub,))
                 threads.append(t)
                 t.start()  #Run Threaded Reqs if no momfile
            for thr in threads:
                thr.join()
            self.createMemFile(str(self.returnPages))
            return self.returnPages
