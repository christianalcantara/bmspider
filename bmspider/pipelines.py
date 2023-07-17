# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from .models import Author, Quote, QuoteTag, Tag, db


class QuotesToScrapePipeline:
    @staticmethod
    def process_item(item, spider):
        with db.atomic():
            author, _ = Author.get_or_create(name=item["author"])
            quote, _ = Quote.get_or_create(text=item["text"], author=author)
            for name in item["tags"]:
                tag, _ = Tag.get_or_create(name=name)
                QuoteTag.get_or_create(quote=quote, tag=tag)
        return item
