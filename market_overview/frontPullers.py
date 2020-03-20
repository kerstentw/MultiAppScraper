import requests
import json
import config
from BeautifulSoup import BeautifulSoup as BS
import traceback

PROXY_DICT = {"http" : "http://kerstentw:Vulcano1$@world.proxymesh.com:31280","https" : "http://kerstentw:Vulcano1$@world.proxymesh.com:31280"}



class CoinCodexFront(object):
    def __init__(self):
        self.endpoint = "https://coincodex.com/apps/coincodex/cache/all_coins.json"

    def __normalizeListToSummaries(self, _asset_struct):
        normalized_struct = {}
        normalized_struct["symbol"] = _asset_struct["symbol"]
        normalized_struct["current_price"] = "Unlisted" if str(_asset_struct["last_price_usd"]) == "None" else str(_asset_struct["last_price_usd"])
        normalized_struct["percent_change"] = str(_asset_struct["price_change_1D_percent"]) + "%"
        normalized_struct["volume"] = str(_asset_struct["volume_24_usd"])
        normalized_struct["slug_name"] = _asset_struct["shortname"]
        normalized_struct["name"] = _asset_struct["name"]
        normalized_struct["market_cap"] = str(float(_asset_struct["last_price_usd"]) * float(_asset_struct["supply"])) if _asset_struct.get("last_price_usd") and _asset_struct.get("supply") else "-"


        return normalized_struct

    def arrangeByMarketCap(self,_summary_list):
        final_list = []
        bottom_barrel = []
        indexer = dict()
        ref_list = []

        for price in _summary_list:
            idx = _summary_list.index(price)
            try:
                mkt_cap = float(price.get("market_cap"))
                ref_list.append(mkt_cap)

            except:
                bottom_barrel.append(price)

        ref_list.sort()
        arranged = ref_list[::-1]

        for _index in arranged:
            for price in _summary_list:
                if price.get("market_cap") == str(_index):
                    final_list.append(price)
                    break
                else:
                    pass

        final_list.extend(bottom_barrel)

        return final_list


    def filterNone(self, _price_obj):
        if _price_obj.get("market_cap") in ["-",None]:
            return None
        else:
            return _price_obj

    def returnNormalizedStructuresAsDictList(self, _base_struct):
        normalized_list = []
        for _asset in _base_struct:
            if _asset["name"] in config.BLACKLIST:
                continue

            normalized_list.append(self.__normalizeListToSummaries(_asset))
        return normalized_list

    def makeRequestToAPIAndReturnDICT(self):#proxies = PROXY_DICT
        resp = requests.get(self.endpoint)
        json_struct = json.loads(resp.content)
        return json_struct

    def returnNormalizedListOfJSON(self):
        main_struct = self.makeRequestToAPIAndReturnDICT()
        dict_list = self.returnNormalizedStructuresAsDictList(main_struct)
        pidict_list = self.arrangeByMarketCap(dict_list)
        return json.dumps(dict_list)


class CoinMarketCapFrontScrape(object):
    def __init__(self):
        self.endpoint = "https://api.coinmarketcap.com/v1/ticker/?limit=100"

    def __normalizeListToSummaries(self, _asset_struct):
        normalized_struct = {}
        normalized_struct["symbol"] = _asset_struct["symbol"]
        normalized_struct["current_price"] = _asset_struct["price_usd"]
        normalized_struct["percent_change"] = str(_asset_struct["percent_change_24h"]) + "%"
        normalized_struct["volume"] = _asset_struct["24h_volume_usd"]
        normalized_struct["slug_name"] = _asset_struct["id"]
        normalized_struct["name"] = _asset_struct["name"]

        return normalized_struct


    def returnNormalizedStructuresAsDictList(self, _base_struct):
        normalized_list = []
        for _asset in _base_struct:
            normalized_list.append(self.__normalizeListToSummaries(_asset))
        return normalized_list

    def makeRequestToAPIAndReturnDICT(self):
        resp = requests.get(self.endpoint)
        json_struct = json.loads(resp.content)
        return json_struct

    def returnNormalizedListOfJSON(self):
        main_struct = self.makeRequestToAPIAndReturnDICT()
        dict_list = self.returnNormalizedStructuresAsDictList(main_struct)
        return json.dumps(dict_list)



class CoinMarketCapFront(object):
    def __init__(self):
        self.endpoint = "https://api.coinmarketcap.com/v1/ticker/?limit=500"

    def __normalizeListToSummaries(self, _asset_struct):
        normalized_struct = {}
        normalized_struct["symbol"] = _asset_struct["symbol"]
        normalized_struct["current_price"] = _asset_struct["price_usd"]
        normalized_struct["percent_change"] = str(_asset_struct["percent_change_24h"]) + "%"
        normalized_struct["volume"] = _asset_struct["24h_volume_usd"]
        normalized_struct["slug_name"] = _asset_struct["id"]
        normalized_struct["name"] = _asset_struct["name"]
        normalized_struct["market_cap"] = _asset_struct["market_cap_usd"]

        return normalized_struct


    def returnNormalizedStructuresAsDictList(self, _base_struct):
        normalized_list = []
        for _asset in _base_struct:
            normalized_list.append(self.__normalizeListToSummaries(_asset))
        return normalized_list

    def makeRequestToAPIAndReturnDICT(self):
        resp = requests.get(self.endpoint)
        json_struct = json.loads(resp.content)
        return json_struct

    def returnNormalizedListOfJSON(self):
        main_struct = self.makeRequestToAPIAndReturnDICT()
        dict_list = self.returnNormalizedStructuresAsDictList(main_struct)
        return json.dumps(dict_list)



class CoinCapFront(object):
    def __init__(self):
        self.endpoint = "http://coincap.io/front"

    def __normalizeListToSummaries(self, _asset_struct):
        normalized_struct = {}
        normalized_struct["symbol"] = _asset_struct["short"]
        normalized_struct["current_price"] = _asset_struct["price"]
        normalized_struct["percent_change"] = str(_asset_struct["perc"]) + "%"
        normalized_struct["volume"] = _asset_struct["volume"]
        normalized_struct["slug_name"] = _asset_struct["long"].lower()
        normalized_struct["name"] = _asset_struct["long"]

        return normalized_struct


    def returnNormalizedStructuresAsDictList(self, _base_struct):
        normalized_list = []
        for _asset in _base_struct:
            normalized_list.append(self.__normalizeListToSummaries(_asset))
        return normalized_list

    def makeRequestToAPIAndReturnDICT(self):
        resp = requests.get(self.endpoint)
        json_struct = json.loads(resp.content)
        return json_struct

    def returnNormalizedListOfJSON(self):
        main_struct = self.makeRequestToAPIAndReturnDICT()
        dict_list = self.returnNormalizedStructuresAsDictList(main_struct)
        return json.dumps(dict_list)



class ChainFXFront(object):
    def __init__(self):
        self.endpoint = "https://onchainfx.com/matrix/get_initial_table_data/9bf0f614e9bd1f93a242cb67ea5ec61ea70e334df36c3766ea273f026509ebd4/root"

    def __normalizeListToSummaries(self, _asset_struct):
        normalized_struct = {}
        normalized_struct["symbol"] = _asset_struct[3]["symbol"]
        normalized_struct["current_price"] = _asset_struct[4]
        normalized_struct["percent_change"] = str(_asset_struct[6]) + "%"
        normalized_struct["volume"] = _asset_struct[14]
        normalized_struct["slug_name"] = _asset_struct[3]["slug"]
        normalized_struct["name"] = _asset_struct[3]["name"]

        return normalized_struct


    def returnNormalizedStructuresAsDictList(self, _base_struct):
        normalized_list = []
        for _asset in _base_struct:
            normalized_list.append(self.__normalizeListToSummaries(_asset))
        return normalized_list

    def makeRequestToAPIAndReturnDICT(self):
        resp = requests.get(self.endpoint)
        json_struct = json.loads(resp.content)
        return json_struct

    def returnNormalizedListOfJSON(self):
        main_struct = self.makeRequestToAPIAndReturnDICT()
        dict_list = self.returnNormalizedStructuresAsDictList(main_struct["data"]["data"])
        return json.dumps(dict_list)

FrontPullerDirectory = {
  "coincodex" : CoinCodexFront,
  "coinmarketcap" : CoinMarketCapFront,
  "coincap" : CoinCapFront,
  "chainfx" : ChainFXFront
}
