from datetime import datetime

import scrapy

from ..items import QuoteItem


class QuotesToScrape(scrapy.Spider):
    name = "quotestoscrape"
    start_urls = [
        "http://quotes.toscrape.com/",
    ]
    quotes_xpath = "//div[@itemscope]"
    text_xpath = './span[@itemprop="text"]/text()'
    author_xpath = './/small[@itemprop="author"]/text()'
    tags_xpath = './/div[@class="tags"]/a[@class="tag"]/text()'
    next_page_xpath = '//li[@class="next"]/a/@href'

    def parse(self, response):
        start_time = datetime.now()

        for quote in response.xpath(self.quotes_xpath):
            quote_item = QuoteItem()
            quote_item["text"] = quote.xpath(self.text_xpath).extract_first()
            quote_item["author"] = quote.xpath(self.author_xpath).extract_first()
            quote_item["tags"] = quote.xpath(self.tags_xpath).extract()
            yield quote_item

        next_page_url = response.xpath(self.next_page_xpath).extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

        end_time_time = datetime.now()
        exec_time = end_time_time - start_time
        self.logger.info(f"Time of execution: {exec_time}")
