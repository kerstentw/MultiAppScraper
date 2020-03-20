import requests
import config

class GlobalCoinCaps(object):
    def __init__(self):
        pass

    def makeRequest(self, _url, _headers):
        resp = requests.get(_url, headers = _headers or {})
        return resp.json()

    def getCMCGlobal(self):
        ret_dict = {}
        """
        {u'data': {u'quotes':
            {u'USD': {
             u'total_volume_24h': 13703146199.0,
             u'total_market_cap': 244021075161.0}},
             u'last_updated': 1529837976,
             u'bitcoin_percentage_of_market_cap': 41.71,
             u'active_cryptocurrencies': 1586,
             u'active_markets': 11221
             },
         u'metadata': {u'timestamp': 1529837734, u'error': None}}
        """

        resp = self.makeRequest(config.ENDPOINTS["CMC_GLOBAL"],None)["data"]
        ret_dict["bitcoin_percentage_of_market_cap"] = resp["bitcoin_percentage_of_market_cap"]
        ret_dict["total_market_cap"] = resp["quotes"]["USD"]["total_market_cap"]
        ret_dict["total_volume_24h"] = resp["quotes"]["USD"]["total_volume_24h"]

        return ret_dict

    def getCFXGlobal(self):
        """
        {u'total_marketcap': u'$229,856,984,415',
           u'index_data': {u'bletchley40':
            {u'name': u'bletchley40',
            u'timestamp': 1529837912,
             u'updatedAt': u'2018-06-24T10:58:34.431Z',
             u'full_quote': None, u'value': 160.95,
             u'change_percent': -9.18,
             u'source': 1,
             u'meta': {},
             u'timeframe': u'DAILY',
             u'id': u'5b2f795a8c60d95f7853d251',
             u'createdAt': u'2018-06-24T10:58:34.431Z'},
             u'bletchley10': {u'name': u'bletchley10',
              u'timestamp': 1529837912,
              u'updatedAt': u'2018-06-24T10:58:34.429Z',
              u'full_quote': None,
              u'value': 798.73,
              u'change_percent': -4.85,
              u'source': 1,
              u'meta': {},
              u'timeframe': u'DAILY',
               u'id': u'5b2f795a8c60d95f7853d24f',
               u'createdAt': u'2018-06-24T10:58:34.429Z'},
               u'bletchley20': {u'name': u'bletchley20',
               u'timestamp': 1529837912,
               u'updatedAt': u'2018-06-24T10:58:34.430Z',
               u'full_quote': None, u'value': 1028.66,
               u'change_percent': -7.7,
               u'source': 1, u'meta': {},
                u'timeframe':
                u'DAILY',
                u'id': u'5b2f795a8c60d95f7853d250',
                u'createdAt': u'2018-06-24T10:58:34.430Z'}
                        },
           u'market_data_last_updated': 1529837912,
           u'pid': 1,
           u'total_marketcap_raw': 229856984415,
           u'bitcoin_dominance': u'44.13%',
           u'homepage_msg': u'',
           u'updatedAt': u'2018-06-24T10:58:32.787Z',
           u'total_y2050_marketcap_raw': 369543315939,
           u'id': u'59d1a4b4d28b63aa5a22efde',
           u'createdAt': u'2017-10-02T02:30:12.470Z',
           u'total_y2050_marketcap': u'$369,543,315,939'
        }
        """

        resp = self.makeRequest(config.ENDPOINTS["CFX_GLOBAL"],None)
        meta = resp["data"]["meta"]

        meta["bitcoin_dominance"]
        meta["total_marketcap_raw"]

        return resp["data"]["meta"]

    def getCNNGlobal(self):
        """
        {u'bitcoin_percentage_of_market_cap': 41.71,
        u'last_updated': 1529837976,
        u'total_market_cap_usd': 244021075161.0,
        u'active_markets': 11221,
        u'active_assets': 794,
        u'active_currencies': 792,
        u'total_24h_volume_usd': 13703146199.0}
        """
        resp = self.makeRequest(config.ENDPOINTS["CNauts_GLOBAL"], config.headers["CNauts_GLOBAL"])
        return resp

    def getIndexes(self):
        resp = self.makeRequest(config.ENDPOINTS["CFX_GLOBAL"],None)
        return resp["data"]["meta"]["index_data"]

    def getAll(self):
        global_data = {
            "global" : self.getCMCGlobal(),
            #"indexes" : self.getIndexes(),
        }
        return global_data
