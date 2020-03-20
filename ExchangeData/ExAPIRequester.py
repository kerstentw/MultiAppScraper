import requests
import json
import base64
import hashlib
import time #for nonce
import hmac

class BitfinexRequester(object):
    def __init__(self,_endpoint,_payload,_api_key, _secret):
        self.endpoint = _endpoint
        self.api_key = _api_key
        self.api_secret = _secret
        self.payload = _payload
        self.payload["request"] = _endpoint
        print "DICKS::: %s" % self.payload

        self.json_payload = json.dumps(self.payload)
        self.b64_payload = str(base64.b64encode(self.json_payload))

        self.hashed_payload = hashlib.sha384(_secret + self.b64_payload)
        #self.hashed_payload.update(self.b64_payload)
        self.signature = self.hashed_payload.hexdigest()
        print "GEN SIG: %s" % self.signature


    def buildBFXSignature(self):
        payload = base64.standard_b64encode(json.dumps(self.payload).encode("utf-8"))
        print payload
        hmacHash = hmac.new(self.api_secret.encode("utf-8"), payload, hashlib.sha384)
        sig = hmacHash.hexdigest()

        print sig
        return {"payload": payload,"signature": sig}


    def buildBFXHeader(self):

        sig_dict = self.buildBFXSignature()

        _header = {
            "request" : self.endpoint,
            "X-BFX-APIKEY" : self.api_key,
            "X-BFX-PAYLOAD" : sig_dict["payload"],
            "X-BFX-SIGNATURE" : sig_dict["signature"]
        }

        return _header



    def makeRequest(self, _endpoint, _data=None):
        _data = {"request":self.endpoint}
        resp = requests.post(self.endpoint, data=_data,headers=self.buildBFXHeader())
        if resp.ok:
            return json.loads(resp)
        else:
            print resp.content
            return None
