import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import CloseSpider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from os import curdir, sep
from os.path import curdir

import scrapy
import re
import json
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.spiders import BaseSpider
from scrapy.http import Request

# DOMAIN = 'towardsdatascience.com/tagged/python'
DOMAIN = 'en.wikipedia.org'
URL = 'https://%s' % DOMAIN

ALL_URLs = []
MAX_URLS_TO_CRAWL = 10000


def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)


class ArticleSpider(CrawlSpider):
    name = "article"

    def parse(self, response):
        # content = response.xpath(".//div[@class='entry-content']/descendant::text()").extract()
        array_of_texts = response.xpath('//p/text()').extract()
        title = response.xpath('//body/div[@class="mw-body"]/h1/text()').extract()

        name = "_".join(map(str, title))
        name = name.replace(" ", "_")
        if title:
            try:
                f = open(curdir + "/files/" + name + '.txt', 'wb')
                for line in array_of_texts:
                    f.write(line.encode("utf-8"))
                    f.write("\n".encode("utf-8"))

                f.close()
            except IOError:
                print("Error opening file!")


class MySpider(CrawlSpider):
    count = 0
    name = DOMAIN
    allowed_domains = [DOMAIN]
    start_urls = [
        URL
    ]

    def parse(self, response):
        url_arr = []

        hxs = Selector(response)
        html_body = str(response.body)
        # print(html_body)

        # all = list(find_all(html_body, 'href="http'))       #regular sites
        all_occurrences = list(find_all(html_body, 'href="'))  # wikipedia sites

        for val in all_occurrences:
            # temp_url = ""

            temp_url = "https://en.wikipedia.org"  # wikipedia sites
            index = val + 6
            while html_body[index] != '"':
                temp_url += html_body[index]
                index += 1
            url_arr.append(temp_url)

        for one_url in hxs.xpath('//a/@href').extract():
            if self.count > MAX_URLS_TO_CRAWL:
                raise CloseSpider('bandwidth_exceeded')
                return
            self.count += 1
            # all_occurrences = list(find_all(html_body, 'href="'))  # wikipedia sites

            # for val in all_occurrences:
            #     # temp_url = ""
            #
            #     temp_url = "https://en.wikipedia.org"  # wikipedia sites
            #     index = val + 6
            #     while html_body[index] != '"':
            #         temp_url += html_body[index]
            #         index += 1
            #         ALL_URLs.append(temp_url)

            if not (one_url.startswith('http://') or one_url.startswith('https://')):
                one_url = URL + one_url
                url_arr.append(one_url)
                ALL_URLs.append(one_url)
                if one_url is not None:
                    next_page = response.urljoin(one_url)
                    yield scrapy.Request(next_page, callback=self.parse)

            else:
                url_arr.append(one_url)
                ALL_URLs.append(one_url)
                if one_url is not None:
                    next_page = response.urljoin(one_url)
                    yield scrapy.Request(next_page, callback=self.parse)
                url_arr.append(one_url)

        # for one_url in url_arr:
        #     if self.count < MAX_URLS_TO_CRAWL:
        #         self.count += 1
        #         # print(one_url)
        #         ALL_URLs.append(one_url)
        #         # test = yield Request(url, callback=self.parse_text)
        #         # return test, None
        #         # yield Request(url, callback=self.parse_text)
        #         if one_url is not None:
        #             next_page = response.urljoin(one_url)
        #             yield scrapy.Request(next_page, callback=self.parse)
        #
        #         # yield Request(one_url, callback=self.parse)
        #     else:
        #         return


# url = ['https://en.wikipedia.org/wiki/Sphere', 'https://en.wikipedia.org/wiki/Celestial_sphere']

# process = CrawlerProcess()
# process = CrawlerProcess({
#     'USER_AGENT': 'Mozilla/5.0 (compatible; MSIE 7.0; Windows NT 5.1)'
#     # 'USER_AGENT': 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405'
# })
# process.crawl(ArticleSpider, start_urls=url)
# process.crawl(MySpider)
# process.start()  # the script will block here until all crawling jobs are finished

runner = CrawlerRunner()


@defer.inlineCallbacks
def crawl():
    yield runner.crawl(MySpider)
    yield runner.crawl(ArticleSpider, start_urls=ALL_URLs)

    reactor.stop()


crawl()
reactor.run()

for url in ALL_URLs:
    print(url)
print(ALL_URLs.__len__())
# the script will block here until the last crawl call is finished
