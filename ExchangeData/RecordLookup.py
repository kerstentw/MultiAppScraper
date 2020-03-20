from ExAPIRequester import BitfinexRequester
import traceback

class LookUpBitfinex(object):

    def __init__(self):
        self.requester = BitfinexRequester

    def LookUp(self,_api_key, _api_secret,_limit = 200):
        endpoint = "https://api.bitfinex.com/v1/offers/hist"
        payload = {"limit" : _limit}
        req_obj = self.requester(endpoint, payload, _api_key, _api_secret)
        resp = req_obj.makeRequest(endpoint)
        if resp:
            return resp
        else:
            return {"error":"request error"}

def test():
    LUB = LookUpBitfinex()
    l = LUB.LookUp("rPoLQVoKyaRhfEpNXd8eWvaukx1fSw96raUOOgNTvH1","dIBpyVqcObJlIYAYQGcvj4Np9rLs3PcRmzapdwYHupR")
    print l
