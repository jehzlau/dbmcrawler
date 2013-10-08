from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from dbmcrawler.items import PDAFItemLoader, Legislator
import re


class PDAFCrawler(BaseSpider):
    name = 'pdaf'
    allowed_domains = ['dbm.gov.ph']
    start_urls = ['http://pdaf.dbm.gov.ph/index.php?r=Site/Ajax/proc/loadListPerLegislator/fy/2013&_=1381158890182']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        legislators_hxs = hxs.select("//table/tr/td[@nowrap='nowrap' and position() = 2 and not(@class='td_right')]/..");
        for legislator_hxs in legislators_hxs:
            legislator = Legislator()
            regex = re.search("'(\d+)', '(.*)','(\d+)'", legislator_hxs.select('@onclick').extract()[0])
            legislator['legislator_id'] = regex.group(1)
            legislator['legislator_type'] = regex.group(2)
            legislator['district_id'] = regex.group(3)
            legislator['name'] = legislator_hxs.select('td[1]/text()').extract()[0].strip()
            legislator['continuing'] = legislator_hxs.select('td[3]/text()').extract()[0].strip()
            legislator['new'] = legislator_hxs.select('td[4]/text()').extract()[0].strip()
            legislator['total'] = legislator_hxs.select('td[5]/text()').extract()[0].strip()
            yield legislator

            if(legislator['legislator_type'] == "District Representative"):
                req = Request("http://pdaf.dbm.gov.ph/index.php?r=Site/District_breakdown_rel2/legislatorId/" + legislator['legislator_id'] + "/districtID/" + legislator['district_id'] + "/fy/2013", callback=self.parse_legislator)
            elif(legislator['legislator_type'] == "Senator"):
                req = Request("http://pdaf.dbm.gov.ph/index.php?r=Site/Partylist_breakdown2/legislatorId/" + legislator['legislator_id'] + "/districtID/" + legislator['district_id'] + "/fy/2013", callback=self.parse_legislator)
            elif(legislator['legislator_type'] == "PartyList Representative"):
                req = Request("http://pdaf.dbm.gov.ph/index.php?r=Site/Upperhouse_breakdown/legislatorId/" + legislator['legislator_id'] + "/fy/2013", callback=self.parse_legislator)
            req.meta['legislator'] = legislator
            yield req


    def parse_legislator(self, response):
        hxs = HtmlXPathSelector(response)
        if(response.meta['legislator']['legislator_type'] == 'District Representative'):
            projects_hxs = hxs.select('//tr[contains(@onclick, "breakDown")]')
            for project_hxs in projects_hxs:
                loader = PDAFItemLoader(selector=project_hxs)
                loader.add_xpath('description', 'td[1]/node()')
                loader.add_xpath('recipient', 'td[2]/node()')
                loader.add_xpath('city', 'td[3]/node()')
                loader.add_xpath('unit', 'td[4]/node()')
                loader.add_xpath('release_date', 'td[5]/node()')
                loader.add_xpath('total', 'td[6]/node()')
                loader.add_value('legislator_id', response.meta['legislator']['legislator_id'])
                return loader.load_item()