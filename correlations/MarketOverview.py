import requests
from BeautifulSoup import BeautifulSoup as BS
import config
import sys
sys.path.append("..")
from utils import cmc_slug_abbrs
from utils.Memoizer import Memoizer
from CorrelationsInterface import CMCCorrelationInterface
import time
from multiprocessing import Pool

id_list = ["gainers-1h", "gainers-24h", "gainers-7d",  "losers-7d","losers-1h", "losers-24h", ]


class MarketOverview(object):

    date_conversions = {
        "1d"   : 86400000,
        "1w"  : 604800000,
        "1m" : 2592000000,
        "1y"  : 31104000000,
        "5y" : 155520000000,
    }

    def __init__(self, _increment = "1day"):
        self.increment = _increment
        self.Memoize = Memoizer("toptwenty" + _increment, 600)
        self.threads = []
        self.correlations = None

    def CMCgrabGainersLosersAbbr(self, _page_html, _id_list = id_list):

        gain_losers = {}
        soup = BS(_page_html)
        for _id in _id_list:
            main_container = soup.find("div", {"id":str(_id)})
            abbrs = main_container.findAll("td",{"class":"text-left"})
            gain_losers[_id]= [abbr.text for abbr in abbrs]
             #= [abbr for abbr in abbr_list if abbr]

        return gain_losers

    def requestPage(self, _query = config.CMC_GAINERS_LOSERS):
        return requests.get(_query, headers = {"user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"}, proxies = config.PROXY_DICT)

    def getLosersAndGainers(self, _mode = "cmc"):
        html_string = self.requestPage(config.CMC_GAINERS_LOSERS).content
        parsers = {"cmc" : self.CMCgrabGainersLosersAbbr}
        return parsers[_mode](html_string)

    def compareLosersAndGainersToBase(self, _start_timestamp, _end_timestamp, _base_asset_abbr):
        Memoize = Memoizer("losers_gainers", 600)
        correlations = {}
        CMC_cor = CMCCorrelationInterface()
        gainers_losers = self.getLosersAndGainers()
        semaphore = []
        CMC_cor = CMCCorrelationInterface() #Build Interface

        if Memoize.needsScrape():
            for _key in gainers_losers:

                if gainers_losers[_key]:
                    CMC_cor.baseThreadRequester(_base_asset_abbr, _start_timestamp,
                    _end_timestamp, gainers_losers[_key])

                    correlations[_key] = CMC_cor.correlations
                else:
                    pass

            correlations["base"] = _base_asset_abbr
            Memoize.writeSocket(correlations)
            return correlations
        else:
            correlations = Memoize.readSocket().get("data")
            return correlations


        return CMC_cor.correlations

    def getOnChainFXTopTwenty(self):
        resp = requests.get(config.ONCHAINFX)
        if resp.ok:
            top_twenty = resp.json()["data"]["data"][:20]
            return [p[3]['symbol'].encode('utf-8') for p in top_twenty]
        else:
            return config.FALLBACK

    def getTopTwenty(self):
        try:
            limit = 20
            endpoint = config.CMC_TICKER.format(limit = limit)
            ticker_data = self.requestPage(endpoint).json().get("data")
            top_twenty = [(ticker_data[_id].get("rank"), ticker_data[_id].get("symbol")) for _id in ticker_data if ticker_data[_id].get("rank") <= limit]
            top_twenty.sort()
            return [slug[1] for slug in top_twenty]
        except:
            return config.FALLBACK

    def buildGainerLoserPage(self, _base):
        lg_struct = self.compareLosersAndGainersToBase(int(time.time() * 1000) - 86400000,
                  int(time.time() * 1000), _base)
        return lg_struct

    def sanitizeLargeStruct(self, _lg_struct):
        pass

    def buildTop20Page(self):
        offset = self.date_conversions.get(self.increment) or self.date_conversions.get("1d")


        # abbr_list = self.getTopTwenty()
        abbr_list = self.getOnChainFXTopTwenty()
        CMC_cor = CMCCorrelationInterface()
        _start_timestamp = int(time.time() * 1000) - offset
        _end_timestamp = int(time.time() * 1000)
        cur_threads = []

        if self.Memoize.needsScrape():
            "NO STRUCT, CREATING BASE"

            CMC_cor.threadRequester( _start_timestamp,
                                _end_timestamp, abbr_list)

            self.correlations = CMC_cor.correlations
            self.correlations["ordered_list"] = abbr_list

            self.Memoize.writeSocket(self.correlations)
            return self.correlations

        else:
            self.correlations = self.Memoize.readSocket().get("data")
            return self.correlations

def test():
    MO = MarketOverview()
    return MO.buildGainerLoserPage("ETH")
