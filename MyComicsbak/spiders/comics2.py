import scrapy
import os
import urllib
import zlib
from bs4 import BeautifulSoup

class Comics(scrapy.Spider):

	name = "comics"
	# allowed_domains = ['http://www.xeall.com']
	# start_urls = ['http://www.xeall.com/shenshi/p20.html']

	def start_requests(self):
		urls = ['http://18h.mm-cg.com/18H_5717.html']
		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)
			# yield scrapy.Request(url=url, callback=self.comics_parse)

	def parse(self, response):
		# 请求返回的html源码
		content = response.body;
		if not content:
			self.log('parse body error.')
			return

		# 用BeautifulSoup库进行节点的解析
		soup = BeautifulSoup(content, "html5lib")
		print(soup)
