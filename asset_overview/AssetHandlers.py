from sys import path
import requests
import json
from cmc_slug_abbrs import CMC_SLUG_ABBRS as cmc_convert
from ccodex_slug_abbrs import COINCODEX_ABBR_TO_SLUGS as ccodex_convert
path.append("..")

class Requester(object):
    header = {}

    def requestInfoForPage(self,*query_strings, **KWARGS):
        #KWARGS is unused for now
        return [requests.get(_q, headers = self.header for _q in query_strings]

    def returnCoinCapHeader(self):
          header = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Cookie": "__cfduid=d1d1a0efdab877fb73c5ec12b5e2eb9e81523085929; _ga=GA1.2.1504417739.1523085935; _gid=GA1.2.1988803500.1524421912; io=3AVgFLWc_RImmkjGBQMg",
            "Host": "coincap.io",
            "Pragma": "no-cache",
            "Referer": "http://coincap.io/BTC",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
          }

class CoinCodexAsset(Requester):

    """
    sample: https://coincodex.com/api/coincodex/get_coin/BTC/?t=5081402
    sample2: https://coincodex.com/api/coincodex/get_coin_history/BTC/2018-04-16/2018-04-23/600?t=5081402
    sample2["BTC"]
    """


    def convertTimeStampToCoinCodexString(self, _time_stamp):
        return time.strftime("%Y-%m-%d",time.localtime(int(_time_stamp)))

    def convertAbbrToSlug(self, _abbr):
        return ccodex_convert.get(_abbr)


    def __init__(self, _asset_abbr, _timestamp_start, _timestamp_end):
        self.infoEndpoint = "https://coincodex.com/crypto/{asset_slug}/"
        #self.infoEndpoint = "https://coincodex.com/api/coincodex/get_coin/{asset_abbr}/?t=5081402"
        self.priceEndpoint = "https://coincodex.com/api/coincodex/get_coin_history/BTC/{date_start}/{date_end}/600?t=5081402"
        self.formatted_price_endpoint = self.infoEndpoint.format(asset_slug = self.convertAbbrToSlug(_asset_abbr))
        self.formatted_info_endpoint = self.infoEndpoint.format(date_start = self.convertTimeStampToCoinCodexString(_timestamp_start),
                                                                date_end = self.convertTimeStampToCoinCodexString(_timestamp_end)
                                                               )
        self.asset_abbr = _asset_abbr


    def normalize_struct(self,_struct):
        normalized_dictionary = {}
        normalized_dictionary["id"] = _struct["shortname"]
        normalized_dictionary["name"] = _struct["name"]
        normalized_dictionary["symbol"] = _struct["symbol"]
        normalized_dictionary["price_usd"] = _struct["last_price_usd"]
        normalized_dictionary["24h_volume_usd"] = _struct["volume_24_usd"]
        normalized_dictionary["percent_change_1h"] = _struct["price_change_1H_percent"]
        normalized_dictionary["percent_change_24h"] = _struct["price_change_1D_percent"]
        normalized_dictionary["percent_change_7d"] = _struct["price_change_7D_percent"]
        normalized_dictionary["last_updated"] = _struct["last_update"]
        return normalized_dictionary




    def returnStructuredShit(self):
        # Shit is JSON object
        asset_summary = {}

        info_resp, price_resp = self.requestInfoForPage(self.infoEndpoint, self.priceEndpoint)
        info_dict = json.loads(info_resp.content)
        price_dict = json.loads(price_resp.content)

        asset_summary["prices"] = price_dict[self.asset_abbr]
        asset_summary.update(info_dict)

        return asset_summary



class CoinMarketCapAsset(Requester):

    """
    sample: https://api.coinmarketcap.com/v1/ticker/bitcoin/
    sample2: https://graphs2.coinmarketcap.com/currencies/bitcoin/1426871960000/1426958360000/
    """

    def convertAbbrToSlug(self, _abbr):
        return cmc_convert.get(_abbr)

    def __init__(self, _asset_abbr, _timestamp_start, _timestamp_end):
        self.infoEndpoint = "https://api.coinmarketcap.com/v1/ticker/{asset_slug}/"
        self.priceEndpoint = "https://graphs2.coinmarketcap.com/currencies/{asset_slug}/{timestamp_start}/{timestamp_end}/"
        self.formatted_price_endpoint = self.infoEndpoint.format(asset_slug = self.convertAbbrToSlug(_asset_abbr))
        self.formatted_info_endpoint = self.infoEndpoint.format(asset_slug = self.convertAbbrToSlug(_asset_abbr),
                                                                timestamp_start = _timestamp_start,
                                                                timestamp_end = _timestamp_end
                                                               )


    def mergeLikeLists(self,listA,listB):
        return [_lisA.extend(lisB[1]) for _lisA,_lisB in zip(listA,listB)]



    def normalizeInfoDict(self,_dict):
        del _dict["rank"]
        del _dict["price_btc"]
        del _dict["market_cap_usd"]
        del _dict["available_supply"]
        del _dict["total_supply"]
        del _dict["max_supply"]
        return _dict


    def returnStructuredShit(self):
        info_resp, price_resp = self.requestInfoForPage(self.formatted_info_endpoint, self.formatted_price_endpoint)
        info_dict, price_dict = json.loads(info_resp.content), json.loads(price_resp.content)

        return_structure = {}
        return_structure["prices"] = self.mergeLikeLists(price_resp["price_usd"], price_resp["volume_usd"])
        return_structure.update(self.normalizeInfoDict(info_dict))

        return return_structure

class CoinCapAsset(object):

    """
    sample: http://coincap.io/front

    """

    def __init__(self):
        self.infoEndpoint = "http://coincap.io/front"



class ChainFXAsset(object):
    """
    sample: https://onchainfx.com/chartdata/bitcoin/daily
    sample: https://onchainfx.com/matrix/get_initial_table_data/0/root
    """

    def __init__(self):
        self.priceEndpoint = "https://onchainfx.com/chartdata/{asset_slug}/daily"



FrontPullerDirectory = {
  "coincodex" : CoinCodexAsset,
  "coinmarketcap" : CoinMarketCapAsset,
  "coincap" : CoinCapAsset,
  "chainfx" : ChainFXAsset
}
