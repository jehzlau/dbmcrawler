# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from scrapy.contrib.loader import XPathItemLoader
from scrapylib.processors import default_input_processor, default_output_processor


class DbmcrawlerItem(Item):
    # define the fields for your item here like:
    # name = Field()
    pass

class Legislator(Item):
    legislator_id = Field()
    legislator_type = Field()
    district_id = Field()
    name = Field()
    continuing = Field()
    new = Field()
    total = Field()

class PDAFItem(Item):
    description = Field()
    recipient = Field()
    city = Field()
    unit = Field()
    release_date = Field()
    total = Field()
    legislator_id = Field()

class PDAFItemLoader(XPathItemLoader):
    default_item_class = PDAFItem
    default_input_processor = default_input_processor
    default_output_processor = default_output_processor