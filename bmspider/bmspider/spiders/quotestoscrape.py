import scrapy

from ..items import QuoteItem


class QuotesToScrape(scrapy.Spider):
    name = "quotestoscrape"
    start_urls = [
        "http://quotes.toscrape.com/",
    ]

    def parse(self, response):
        for quote in response.xpath("//div[@itemscope]"):
            quote_item = QuoteItem()
            quote_item["text"] = quote.xpath('./span[@itemprop="text"]/text()').extract_first()
            quote_item["author"] = quote.xpath('.//small[@itemprop="author"]/text()').extract_first()
            quote_item["tags"] = quote.xpath('.//div[@class="tags"]/a[@class="tag"]/text()').extract()
            yield quote_item

        next_page_url = response.xpath('//li[@class="next"]/a/@href').extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))
