import config
import json
import requests
import time
import datetime
import traceback
import re
from BeautifulSoup import BeautifulSoup as BS

# x = requests.post(api_string,data = "grant_type=client_credentials", headers= {"Authorization":"Basic %s" % key, "Content-Type":"application/x-www-form-urlencoded;charset=UTF-8"})

class TwitterInterface(object):
    url_frame = "https://twitter.com/i/web/status/{_id}"
    user_rex = re.compile("RT (.*)\:")

    def __init__(self):
        self.search_headers = config.search_headers
        self.bearer_token = None

    def setBearerToken(self):
        if self.bearer_token:
            return self.bearer_token

        resp = requests.post(config.TOKEN_ENDPOINT,config.KEY_ACQUISITION_STRING, headers=config.OAUTH_HEADERS)
        bearer_token = json.loads(resp.content).get("access_token")

        if bearer_token:
            self.bearer_token = bearer_token
            return bearer_token

        else:
            return "Error Getting Token: (%s): %s" % (resp.status_code, resp.content)

    def setSearchHeader(self):
        if not self.bearer_token:
            self.setBearerToken()

        self.search_headers["Authorization"] = "Bearer %s" % self.bearer_token


    def convertFromTwitterTime(self,_time_string):
        return time.mktime(datetime.datetime.strptime(_time_string.replace("+0000",""),"%a %b %d %H:%M:%S  %Y").timetuple())


    def filterTwitterResponse(self, _resp_dict):
        return_list = []

        statuses = _resp_dict.get("statuses")

        for status in statuses:

            return_struct = {}
            return_struct["text"] = status.get("text")
            return_struct["retweet_count"] = status.get("retweet_count")
            return_struct["favorite_count"] = status.get("favorite_count")
            return_struct["user_description"] = status.get("user").get("description")
            return_struct["user_followers"] = status.get("user").get("followers_count")


            try:
                return_struct["url"] = self.url_frame.format(_id = status.get("id_str"))
            except:
                return_struct["url"] = "https://twitter.com"
                traceback.print_exc()

            try:
                return_struct["author_screen_name"] = status.get("user").get("screen_name")
                return_struct["author_name"] = status.get("user").get("name")

            except:
                return_struct["author"] = "Twitter.com"
                traceback.print_exc()

            return_struct["timestamp"] = status.get("created_at")

            return_list.append(return_struct)

        return return_list


    def convertTimeStampToHuman(self):
        return datetime.datetime.fromtimestamp(
            int(time.time())
        ).strftime('%Y-%m-%d')

    def searchTwitter(self,_query):
        self.setSearchHeader()
        resp = requests.get(config.SINCE_SEARCH_ENDPOINT.format(query = _query,since = self.convertTimeStampToHuman()), headers = self.search_headers)
        with open("temp_json_sample_twitter.json","w") as my_fil:
            my_fil.write(resp.content)

        return self.filterTwitterResponse(json.loads(resp.content))





class TwitterScraper(object):

    def __init__(self, _endpoint = "https://mobile.twitter.com/avocadobyproof"):
        self.ENDPOINT = _endpoint
        self.soup = None

    def __makeRequestAndReturnSoup(self):
        resp = requests.get(self.ENDPOINT)
        #print resp.content
        self.soup = BS(resp.content)
        return self.soup


    def __getTweetList(self):
        tweet_soups = self.__makeRequestAndReturnSoup()
        return self.soup.findAll("table", {"class":"tweet  "})


    def __scoopHashtags(self, tweet_soup):
        hash_links = tweet_soup.findAll("a",{"class" : "twitter-hashtag dir-ltr"})
        return [{"link" : h["href"], "text" : h.text} for h in hash_links]


    def __getTweetBody(self, tweet_soup):
        return tweet_soup.find("div", {"dir" : "ltr"}).text.replace("#", " #")


    def __getTimestamp(self, tweet_soup):
        return tweet_soup.find("td", {"class": "timestamp"}).text


    def __getUserInfo(self, tweet_soup):
        user_img = tweet_soup.find("img")["src"]
        user_soup = tweet_soup.find("td",{"class" : "user-info"})

        return {
            "img" : user_img,
            "link": user_soup.find("a")["href"],
            "real_name" : user_soup.find("strong").text,
            "username" : user_soup.find("div",{"class" : "username"}).text
            }

    def __getMainLink(self, tweet_soup):
        return tweet_soup.find("span", {"class" : "metadata"}).find("a")["href"]

    def getFirstTwenty(self):
        tweet_list = self.__getTweetList()
        print tweet_list
        processed_tweets = []

        for sup in tweet_list:
            processed_tweets.append(
                {
                    "user_info" : self.__getUserInfo(sup),
                    "link" : self.__getMainLink(sup),
                    "text" : self.__getTweetBody(sup),
                    "hashtags" : self.__scoopHashtags(sup),
                    "timestamp" : self.__getTimestamp(sup)
                })

        return {"tweets" : processed_tweets, "pulltime" : int(time.time()), "number" : len(processed_tweets)}
