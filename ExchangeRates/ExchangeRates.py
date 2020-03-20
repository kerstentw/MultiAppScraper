import json
import requests
from RatesLogger import RatesLogger

class ExchangeRates(object):
    def __init__(self):
        self.endpoint1 = "http://coincap.io/exchange_rates"
        self.log_manager = RatesLogger()

    def getExchangeRateFromEndpoint(self, _base):
        resp = requests.get(self.endpoint1)
        conversion_rates = json.loads(resp.content).get("rates")
        if conversion_rates:
            return conversion_rates[_base]
        else:
            return False

    def getExchangeRateFromFile(self,_base):
        self.log_manager.checkFreshnessAndLog(self.endpoint1)

        with open(self.log_manager.file_name, "r") as my_fil:
            conversion_rates = json.loads(my_fil.read()).get("rates")

        if conversion_rates:
            return conversion_rates[_base]
        else:
            return self.getExchangeRateFromEndpoint(_base)

    def GetExchangeByUSD(self,_asset_abbr, _amnt):
        exchange = self.getExchangeRate(_asset_abbr)
        if exchange:
            return float(exchange) * float(_amnt)
        else:
            return False

    def convertBetweenTwo(self, _from, _to, _amount):
        from_price = float(self.getExchangeRateFromFile(_from))
        to_price = float(self.getExchangeRateFromFile(_to))
        if from_price and to_price:
            return (to_price/from_price) * _amount
