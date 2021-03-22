import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import NordeaItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class NordeaSpider(scrapy.Spider):
	name = 'nordea'
	start_urls = ['https://www.nordea.dk/privat/nyheder/']

	def parse(self, response):
		post_links = response.xpath('//article[@class="article"]//a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		try:
			date = response.xpath('//div[@itemprop="datePublished"]/text()').get().strip()
		except AttributeError:
			date = '-'
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//section[@itemprop="articleBody"]//text()[not (ancestor::div[@class="field field--name-field-factbox-text field--type-text-long field--label-hidden field__item"] or ancestor::div[@class="field-image"] or ancestor::div[@class="share_outer_container"] or ancestor::div[@class="related_article_outer_container"])] | //section[@class="section section--article"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=NordeaItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
