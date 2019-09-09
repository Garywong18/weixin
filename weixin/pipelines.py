# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

class WeixinPipeline(object):
    def open_spider(self,spider):
        self.db = pymysql.connect(host='localhost',user='root',password='123456',port=3306,db='text')
        self.cursor = self.db.cursor()

    def close_spider(self,spider):
        self.db.close()

    def process_item(self, item, spider):
        data = dict(item)
        keys = ','.join(data.keys())
        values = ','.join(['%']*len(data))
        sql = 'insert into weixin (%s) values (%s)' %(keys,values)
        self.cursor.execute(sql,tuple(data.values()))
        self.db.commit()
        return item
