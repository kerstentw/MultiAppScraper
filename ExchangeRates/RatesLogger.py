import os
import json
import time
import requests

class RatesLogger(object):

    def __init__(self):

        self.file_name = "rate_chart.json"
        self.file_keys = ["last_update", "rates"]
        self.cur_log = {}
        self.freshness_tolerance = 86400
        self.logpath = "."
        self.full_file_path = os.path.join(self.logpath, self.file_name)
        self.default_log = {"last_update" : 0, "rates": 0}

    def checkForFile(self):
        if self.file_name in os.listdir("."):
            print os.listdir(".")
            return True
        else:
            return False

    def createLogFile(self):
        with open(self.full_file_path, "w") as my_fil:
            my_fil.write(json.dumps(self.default_log))
            return True


    def createLogFileIfNotExist(self):

        if self.checkForFile():
            pass
        else:
            print "No Logfile Detected, Creating: %s" % self.file_name
            self.createLogFile()

    def readLogFile(self):
        with open(self.full_file_path, "r") as fil:
            self.cur_log = json.loads(fil.read())

        return True

    def writeLogFile(self,_rates_dict):
        struct = {"last_update" : int(time.time()), "rates": _rates_dict}
        with open(self.file_name, "w") as fil:
            fil.write(json.dumps(struct))

        return True

    def checkFreshness(self):
        self.readLogFile()
        if self.cur_log["last_update"] + self.freshness_tolerance < int(time.time()):
            return False
        else:
            return True

    def checkFreshnessAndLog(self,_endpoint):
        self.createLogFileIfNotExist()

        if self.checkFreshness() == False:
            print "Refreshing File"
            resp = requests.get(_endpoint)
            struct = json.loads(resp.content).get("rates")
            self.writeLogFile(struct)
        else:
            return True
