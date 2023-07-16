import scrapy


class QuotesToScrape(scrapy.Spider):
    name = 'quotestoscrape'
    start_urls = [
        'http://quotes.toscrape.com/',
    ]

    def parse(self, response):
        for quote in response.xpath('//div[@itemscope]'):
            yield {
                'text': quote.xpath('./span[@itemprop="text"]/text()').extract_first(),
                'author': quote.xpath('.//small[@itemprop="author"]/text()').extract_first(),
                'tags': quote.xpath('.//div[@class="tags"]/a[@class="tag"]/text()').extract()
            }

        next_page_url = response.xpath('//li[@class="next"]/a/@href').extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))
