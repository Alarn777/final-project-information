from os.path import curdir

import scrapy
import re
import json
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.spiders import BaseSpider
from scrapy.http import Request

# DOMAIN = 'towardsdatascience.com/tagged/python'
DOMAIN = 'en.wikipedia.org/wiki/Main_Page'
URL = 'http://%s' % DOMAIN


class MySpider(scrapy.spiders.Spider):
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
        all = list(find_all(html_body, 'href="'))           # wikipedia sites

        for val in all:
            # temp_url = "http"
            temp_url = "https://en.wikipedia.org"           # wikipedia sites
            index = val + 6
            while html_body[index] != '"':
                temp_url += html_body[index]
                index += 1
            url_arr.append(temp_url)

        # print(url_arr)

        # for link in url_arr:
        #     f.write(link)

        # print(hxs.xpath('//a/@href').extract())

        # var = hxs.xpath('/html/body')

        for url in hxs.xpath('//a/@href').extract():
            if not (url.startswith('http://') or url.startswith('https://')):
                url = URL + url
                url_arr.append(url)
            else:
                url_arr.append(url)

        for url in url_arr:
            if self.count < 1000000:
                self.count += 1
                # test = yield Request(url, callback=self.parse_text)
                # return test, None
                yield Request(url, callback=self.parse_text)
                yield Request(url, callback=self.parse)

            else:
                return

    def parse_text(self, response):
        # content = response.xpath(".//div[@class='entry-content']/descendant::text()").extract()
        array_of_texts = response.xpath('//p/text()').extract()
        title = response.xpath('//div[@class="mw-body"]//@h1').extract()

        if title[0] != "":
            try:
                f = open(curdir + "/files/" + title[0] + '.txt', 'wb')
                for line in array_of_texts:
                    f.write(line.encode("utf-8"))
                    f.write("\n".encode("utf-8"))

                f.close()
            except IOError:
                print("Error opening file!")


def sipder_logic():


    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (compatible; MSIE 7.0; Windows NT 5.1)'
        # 'USER_AGENT': 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405'
    })
    process.crawl(MySpider)
    process.start()


def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)


sipder_logic()
