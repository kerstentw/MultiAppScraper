import json
import random
from sys import path
path.append("..")
from TextualAcquisition.SocialScrapers import TextualScrapersDirectory
import datetime,time
from TextualAcquisition import config
from GoogleNews.GoogleNewsInterface import GoogleNewsRequester
from RSSFeedReader import RSSFeedReader as RSS
from ProofNewsAPI import ProofNewsApi as PNA

class TimeHelper(object):
    def __init__(self):
        pass


class NewsAcquisitionInterface(object):

    """
    This object wraps a news object and gets it ready for return
    """
    def __init__(self, _topic):
        self.news_grabber = TextualScrapersDirectory.get("news_grabber")()
        self.source = "news"
        self.topic = _topic
        self.mapper = config.Mapper()
        self.news_dicts = None
        self.mapped_data = None


    def __grabNewsAPIDict(self):
        news_api_dicts = json.loads(self.news_grabber.getFromNewsApi(self.topic))
        self.news_dicts = news_api_dicts

        return


    def ISO8601ToTimestamp(self,_time_string):

        """Takes ISO 8601 format(string) and converts into epoch time."""

        dt = datetime.datetime.strptime(_time_string,'%Y-%m-%dT%H:%M:%SZ')
        #+\datetime.timedelta(hours=int(_time_string[-5:-3]),
        #minutes=int(_time_string[-2:]))*int(_time_string[-6:-5]+'1')
        seconds = time.mktime(dt.timetuple()) + dt.microsecond/1000000.0

        return int(seconds)


    def __mapAllWithTimestamp(self):
        print self.news_dicts
        self.mapped_data = [self.mapper.map_structure(_data) for _data in self.news_dicts.get("articles")]
        for _data_dict in self.mapped_data:
            _data_dict["when"] = self.ISO8601ToTimestamp(_data_dict["when"])
            _data_dict["type"] = self.source

        return


    def grabNewsAPIAndReturnAsJSON(self):
        self.__grabNewsAPIDict()
        self.__mapAllWithTimestamp()
        return json.dumps(self.mapped_data)



    def grabRSSFeedsAndReturnAsDict(self):
        RSSObj = RSS.RSSFeedReader()
        RSS_dicts = RSSObj.run()
        return RSS_dicts


    def grabNewsAPIAndReturnAsDict(self):
        #SPECIALIZED FOR TICKER NOW
        #if self.news_dicts:
        #return self.news_dicts

        self.__grabNewsAPIDict()
        self.__mapAllWithTimestamp()
        return self.mapped_data


    def grabProofAPIAndReturnAsDict(self):
        news_obj = PNA.ProofNewsApi()
        news_list = news_obj.run()
        return news_list

    def grabTickerFeeds(self):
        rss_list = self.grabRSSFeedsAndReturnAsDict()
        papi_list = self.grabProofAPIAndReturnAsDict()
        combined_list = rss_list + papi_list[2:len(papi_list)/2]
        random.shuffle(combined_list)
        main_list = papi_list[0:2] + combined_list
        return main_list

    def returnRaw(self):
        if self.news_dicts:
            return self.news_dicts
        else:
            self.__grabNewsAPIDict()
            return self.news_dicts



class GoogleNewsInterface(object):

    def __init__(self, _topic = "blockchain", _depth = 5,_raw = False):
        self.topic = _topic
        self.depth = _depth
        self.raw = _raw

    def grabGoogleNews(self):
        G = GoogleNewsRequester(self.topic,self.depth, self.raw)
        return G.getArtList()
