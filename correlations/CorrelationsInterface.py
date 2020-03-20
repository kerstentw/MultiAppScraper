import json
import requests
from sys import path
path.append("..")
from utils import CorrelationGenerator
from utils.cmc_slug_abbrs_updated import CMC_SLUG_ABBRS
import config
import threading
from multiprocessing.pool import ThreadPool

"""
    The correlation Interface is responsible for composing a correlation
    Generator, acquiring data, and returning the correlation data
    to the api.  The interface is where user calls will go.
"""

class CorrelationsInterface(object):

    def determineGrabType(self, _payload_dict):
        pass

    def __init__(self):
        self.base_analytics_endpoint = config.ONCHAINFX
        self.session = requests.Session()
        self.cor_dict = CorrelationGenerator.CorrelationDirectory

    def returnAllCorrelations(self,_setA,_setB):
        correlations = {}
        for _key in self.cor_dict:
            correlations[_key] = self.cor_dict[_key](_setA,setB).returnCorrelation()
        return correlations


    def seeInstalledTypes(self):
        return self.cor_dict.keys()

    def returnSingleCorrelation(self,_setA, _setB, _type = "pearson"):
        cor_obj = self.cor_dict[_type](_setA, _setB)
        return cor_obj.returnCorrelation()





class CMCCorrelationInterface(CorrelationsInterface):

    correlations = {}
    prices = {}
    current_threads = []

    def getBaseAssetPrices(self, _start_timestamp, _end_timestamp, _base_asset_abbr):
        cmc_endpoint = config.CMC_PRICE_ENDPOINT
        _asset_slug = CMC_SLUG_ABBRS.get(_base_asset_abbr)
        query_string = cmc_endpoint.format(start_timestamp = _start_timestamp,
                                           end_timestamp = _end_timestamp,
                                           asset_slug = _asset_slug)

        resp = self.session.get(query_string)
        cmc_base_struct = json.loads(resp.content)
        base_prices =  cmc_base_struct.get("price_usd")

        return base_prices



    def getCMCPrices(self, _interval, _start_timestamp, _end_timestamp, _base_prices, _asset_abbr):
        normalize_cmc_by_price = lambda cmc_prices: [_lis[1] for _lis in cmc_prices]
        self.correlations[_interval] = {}
        cmc_endpoint = config.CMC_PRICE_ENDPOINT
        _asset_slug = CMC_SLUG_ABBRS.get(_asset_abbr)


    cur_prices = {}
    all_prices = {}
    def threadedGrabCMCDataForProcessing(self, _interval, _start_timestamp, _end_timestamp, _type = "pearson"):
        self.correlations[_interval] = {}

        cmc_endpoint = config.CMC_PRICE_ENDPOINT
        _asset_slug = CMC_SLUG_ABBRS.get(_interval)

        if not _asset_slug:
            print "NO ASSET SLUG"
            return

        query_string = cmc_endpoint.format(start_timestamp = _start_timestamp,
                                           end_timestamp = _end_timestamp,
                                           asset_slug = _asset_slug)

        resp = self.session.get(query_string, proxies = config.PROXY_DICT, headers = {"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"})

        #print "%s ::: %s" % (query_string, resp.status_code)
        if not resp.ok:
            print resp.content
            return

        #Place into a class data member
        #Declare Class member

        asset_prices = json.loads(resp.content).get("price_usd")
        self.all_prices.update({_interval : asset_prices})

        return 0


    def threadRequester(self, _start_timestamp, _end_timestamp,  _asset_list, _type = "pearson"):

        local_thread_store = []

        for _asset in _asset_list:
            t = threading.Thread(target= self.threadedGrabCMCDataForProcessing, args = ( _asset, _start_timestamp, _end_timestamp,  "pearson"))
            t.start()
            local_thread_store.append(t)

        for thread in local_thread_store:
            thread.join()

        normalize_cmc_by_price = lambda cmc_prices: [_lis[1] for _lis in cmc_prices]
        cor_obj = self.cor_dict[_type]

        for _key in self.all_prices:
            self.correlations[_key] = {}
            for _compare in self.all_prices:
                correlation_generator = cor_obj(normalize_cmc_by_price(self.all_prices[_key]), normalize_cmc_by_price(self.all_prices[_compare]))
                self.correlations[_key].update({_compare: correlation_generator.returnCorrelation()})


    def baseThreadRequester(self,_base_asset_abbr, _start_timestamp, _end_timestamp, _asset_list, _type = "pearson"):
        self.all_prices = {}
        self.correlations = {}
        cor_obj = self.cor_dict[_type]
        normalize_cmc_by_price = lambda cmc_prices: [_lis[1] for _lis in cmc_prices]

        base_prices = self.getBaseAssetPrices(_start_timestamp, _end_timestamp, _base_asset_abbr)
        local_thread_store = []

        for _asset in _asset_list:
            t = threading.Thread(target= self.threadedGrabCMCDataForProcessing, args = ( _asset, _start_timestamp, _end_timestamp,  "pearson"))
            t.start()
            local_thread_store.append(t)

        for thread in local_thread_store:
            thread.join()

        for _key in self.all_prices:
            if len(self.all_prices[_key]) < 1:
                continue
            correlation_generator = cor_obj(normalize_cmc_by_price(base_prices), normalize_cmc_by_price(self.all_prices[_key]))
            self.correlations[_key] = correlation_generator.returnCorrelation()



    def grabCMCDataForProcessing(self, _start_timestamp, _end_timestamp, _base_asset_abbr, _asset_abbr_list):
        cmc_data_for_correlations = {}
        cmc_data_for_correlations["secondary_assets"] = {}

        cmc_endpoint = config.CMC_PRICE_ENDPOINT
        _asset_slug = CMC_SLUG_ABBRS.get(_base_asset_abbr)

        query_string = cmc_endpoint.format(start_timestamp = _start_timestamp,
                                           end_timestamp = _end_timestamp,
                                           asset_slug = _asset_slug)

        resp = self.session.get(query_string)
        cmc_base_struct = json.loads(resp.content)
        cmc_data_for_correlations["base_asset"] = cmc_base_struct.get("price_usd")


        for _asset in _asset_abbr_list:
            _asset_slug = CMC_SLUG_ABBRS.get(_asset)

            if not _asset_slug:
                continue

            query_string = cmc_endpoint.format(start_timestamp = _start_timestamp,
                                               end_timestamp = _end_timestamp,
                                               asset_slug = _asset_slug)

            resp = self.session.get(query_string, headers = {"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"})

            if not resp.ok:
                print "REQUEST ERROR"
                print resp.content
                continue

            asset_prices = json.loads(resp.content).get("price_usd")
            if asset_prices:
                cmc_data_for_correlations["secondary_assets"][_asset] = asset_prices

        return cmc_data_for_correlations


    def getCMCCorrelations(self, _start_timestamp, _end_timestamp, _base_asset_abbr, _asset_abbr_list, _type = "pearson"):
        normalize_cmc_by_price = lambda cmc_prices: [_lis[1] for _lis in cmc_prices]
        correlations = {}
        cmc_data = self.grabCMCDataForProcessing(_start_timestamp, _end_timestamp, _base_asset_abbr, _asset_abbr_list)
        cor_obj = self.cor_dict[_type]

        for _key in cmc_data["secondary_assets"]:
            correlation_generator = cor_obj(normalize_cmc_by_price(cmc_data["base_asset"]), normalize_cmc_by_price(cmc_data["secondary_assets"][_key]))
            correlations[_key] = correlation_generator.returnCorrelation()

        return correlations


def test():
    import time
    CI = CMCCorrelationInterface()
    print int(time.time()) - 86400
    y = CI.threadRequester(int(time.time() * 1000) - 86400000,int(time.time() * 1000), "ETH", ["BTC", "ETH", "ADA", "XRP","BCH", "EOS", "LTC", "XLM", "TRX", "NEO", "MIOTA","VEN"])
    print y
