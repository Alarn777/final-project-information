import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from os import curdir, sep


class ArticleSpider(scrapy.Spider):
    name = "article"
    # start_urls = ['https://en.wikipedia.org/wiki/Sphere', 'https://en.wikipedia.org/wiki/Celestial_sphere']
    # start_urls = []
    #
    # def __init__(self, urls):
    #     self.start_urls = urls

    def parse(self, response):
        # content = response.xpath(".//div[@class='entry-content']/descendant::text()").extract()
        array_of_texts = response.xpath('//p/text()').extract()
        title = response.xpath('//body/div[@class="mw-body"]/h1/text()').extract()

        name = "_".join(map(str, title))
        name = name.replace(" ", "_")


        # for word in title:
        #     name += word + " "
        if title:
            try:
                f = open(curdir + "/files/" + name + '.txt', 'wb')
                for line in array_of_texts:
                    f.write(line.encode("utf-8"))
                    f.write("\n".encode("utf-8"))

                f.close()
            except IOError:
                print("Error opening file!")
        # yield {'article': ''.join(content)}


# process = CrawlerProcess({
#     'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
# })

url = ['https://en.wikipedia.org/wiki/Sphere', 'https://en.wikipedia.org/wiki/Celestial_sphere']


process = CrawlerProcess()
process.crawl(ArticleSpider, start_urls=url)
process.start()


# process.crawl(ArticleSpider(urls=url))
# process.start()
