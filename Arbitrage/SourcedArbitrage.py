from BeautifulSoup import BeautifulSoup as BS
import requests
import config

class ArbScraper(object):
    def __init__(self):
        pass

    def requestFront(self,_endpoint = ""):
        resp = requests.get(_endpoint)
        return resp



class CryptoCoinCharts(ArbScraper):
    def __init__(self):
        self.endpoint = config.CRYPTOCOINCHART_ARB_ENDPOINT
        self.soup = BS(self.requestFront(self.endpoint).content)
        self.name = "cryptocoincharts"

    def getArbRows(self):
        rows = self.soup.findAll("div",{"class":"arbitrage-row"})
        return rows

    def parseArbElements(self,arb_soup):
        element_struct = {}

        header = arb_soup.find("div", {"class" : "panel-heading"})
        header_elems = [span.text for span in header.findAll("span")]
        mid_head = arb_soup.findAll("div",{"class":"arbitrage-price"})
        mid_elems = [elem.text for elem in mid_head]
        footer = arb_soup.find("p",{"class":"arbitrage-info-text alert"})
        trade_elems = [span.text for span in footer.findAll("span")]

        element_struct["pair"] = header_elems[0]
        element_struct["from"] = header_elems[1]
        element_struct["to"] = header_elems[2]
        element_struct["date"] = header_elems[3]

        element_struct["highest_bid"] = mid_elems[0]
        element_struct["lowest ask"] = mid_elems[1]
        element_struct["spread"] = mid_elems[2]
        element_struct["max_volume"] = mid_elems[3]

        element_struct["buy"] = trade_elems[0]
        element_struct["sell"] = trade_elems[1]
        element_struct["profit"] = trade_elems[2]
        element_struct["source"] = self.name

        return element_struct

    def parseArbPage(self):
        element_list = []
        for elem in self.getArbRows():
            element_list.append(self.parseArbElements(elem))

        return element_list
