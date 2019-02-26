import scrapy
from os import curdir, sep

from crawler import Request
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector, HtmlXPathSelector
from scrapy.http import HtmlResponse
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from os import curdir, sep

DOMAIN = 'towardsdatascience.com/tagged/python'
URL = 'http://%s' % DOMAIN


class PageSpider(scrapy.Spider):
    # name = "page"
    # start_urls = ['https://towardsdatascience.com/tagged/python']

    name = DOMAIN
    allowed_domains = [DOMAIN]
    start_urls = [
        URL
    ]

    def parse(self, response):
        url_arr = []
        hxs = HtmlXPathSelector(response)
        for url in hxs.xpath('//a/@href').extract():
            if not (url.startswith('http://') or url.startswith('https://')):
                url = URL + url
                url_arr.append(url)
            else:
                url_arr.append(url)
            # print(url)
            # yield response.follow(url, callback=self.parse_article)

        print(url_arr)
        for article in url_arr:
            yield response.follow(article, callback=self.parse_article)
        # for article_url in response.css('.entry-title a ::attr("href")').extract():
        #     yield response.follow(article_url, callback=self.parse_article)

    def parse_article(self, response):
        content = response.xpath(".//div[@class='entry-content']/descendant::text()").extract()
        array_of_texts = response.xpath('//p/text()').extract()
        title = response.xpath('//title/text()').extract()

        if title[0] != "":
            try:
                f = open(curdir + "/files/" + title[0] + '.txt', 'wb')
                for line in array_of_texts:
                    f.write(line.encode("utf-8"))
                    f.write("\n".encode("utf-8"))

                f.close()
            except IOError:
                print("Error opening file!")

        yield {'article': ''.join(content)}


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(PageSpider)
process.start()
