# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import re

class CupSpider(scrapy.Spider):
    name = 'cup'
    # 注意是sogou而不是sougou
    # 否则将报错DEBUG: Filtered offsite request to 'weixin.sogou.com'
    allowed_domains = ['sogou.com']
    start_urls = ['https://weixin.sogou.com/weixin?query=%E4%B8%96%E7%95%8C%E6%9D%AF&type=2&sst0=1567922391517&page=1&ie=utf8&w=01019900&dr=1']
    # 重写父类
    def start_requests(self):
        cookies = self.settings['COOKIE']
        cookies = {i.split('=')[0]:i.split('=')[1] for i in cookies.split(';')}
        yield scrapy.Request(
            self.start_urls[0],
            cookies=cookies,
            callback=self.parse
        )

    def parse(self,response):
        news_list = response.xpath("//ul[@class='news-list']/li")
        for news in news_list:
            item = {}
            item['account'] = news.xpath(".//a[@class='account']/text()").extract_first()
            # 获取时间戳
            item['time'] = news.xpath(".//span[@class='s2']//text()").extract_first()
            pat = re.compile('''document.write\(timeConvert\('(\d+)'\)\)''')
            timestamp = pat.search(response.text).group(1)
            # 时间戳转化为字符串
            item['time'] = datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')
            item['href'] = news.xpath(".//div[@class='txt-box']/h3/a/@data-share").extract_first()
            yield scrapy.Request(
                item['href'],
                callback=self.parse_detail,
                meta={'item':item}
            )

        next_page = response.xpath("//a[@id='sogou_next']/@href").extract_first()
        if next_page is not None:
            next_page = 'https://weixin.sogou.com/weixin' + next_page
            yield scrapy.Request(
                next_page,
                callback=self.parse
            )
    def parse_detail(self,response):
        item = response.meta['item']
        item['title'] = response.xpath("//h2[@class='rich_media_title']/text()").extract_first().strip()
        item['content'] = response.xpath("//div[@id='js_content']//text()").extract()
        item['content'] = ','.join(item['content']).strip()
        yield item
