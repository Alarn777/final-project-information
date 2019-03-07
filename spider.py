import string
from os.path import curdir
import string
import unicodedata
from os.path import curdir

import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.exceptions import CloseSpider
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider
from twisted.internet import reactor, defer

DOMAIN = 'en.wikipedia.org'
# DOMAIN = "scholar.google.com"
URL = 'https://%s' % DOMAIN

ALL_URLs = []
MAX_URLS_TO_CRAWL = 100


def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)


class ArticleSpider(CrawlSpider):
    name = "article"

    def removeDisallowedFilenameChars(self, filename):
        validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
        return ''.join(c for c in cleanedFilename if c in validFilenameChars)

    def parse(self, response):
        array_of_texts = response.xpath('//p/text()').extract()
        title = response.xpath('//body/div[@class="mw-body"]/h1/text()').extract()       # for wikipedia
        name = "_".join(map(str, title))
        name = name.replace(" ", "_")
        name = name.replace("/", "_")
        validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        cleanedFilename = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore')
        name = cleanedFilename.decode("utf-8")

        if is_ascii(name):
            if title:
                try:
                    f = open(curdir + "/source/" + name + '.txt', 'wb')
                    for line in array_of_texts:
                        for char in line:
                            if is_ascii(char):
                                f.write(char.encode("utf-8"))
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
        # all = list(find_all(html_body, 'href="http'))       #regular sites
        all_occurrences = list(find_all(html_body, 'href="'))  # wikipedia sites

        for val in all_occurrences:
            temp_url = "https://en.wikipedia.org"  # wikipedia sites
            index = val + 6
            while html_body[index] != '"':
                temp_url += html_body[index]
                index += 1
            url_arr.append(temp_url)

        for one_url in hxs.xpath('//a/@href').extract():
            if self.count > MAX_URLS_TO_CRAWL:
                raise CloseSpider('bandwidth_exceeded')

            self.count += 1

            if not (one_url.startswith('http://') or one_url.startswith('https://')):
                one_url = URL + one_url
                url_arr.append(one_url)
                ALL_URLs.append(one_url)
                if one_url is not None:
                    next_page = response.urljoin(one_url)
                    print(next_page)                                                       # print
                    yield scrapy.Request(next_page, callback=self.parse)

            else:
                url_arr.append(one_url)
                ALL_URLs.append(one_url)
                if one_url is not None:
                    next_page = response.urljoin(one_url)
                    print(next_page)                                                       # print
                    yield scrapy.Request(next_page, callback=self.parse)
                url_arr.append(one_url)


runner = CrawlerRunner()


@defer.inlineCallbacks
def crawl():
    yield runner.crawl(MySpider)
    yield runner.crawl(ArticleSpider, start_urls=ALL_URLs)
    reactor.stop()


def run_spider():
    crawl()
    reactor.run()


# the script will block here until the last crawl call is finished
def is_ascii(s):
    return all(ord(c) < 128 for c in s)



