# Define your item pipelines here
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import os
from urllib.parse import urlparse

import scrapy
from pymongo import MongoClient

class LeroyDataProcess:
    def process_item(self, item, spider):
        n = 7
        w_desc = {}
        item['description'] = [line.strip() for line in item['description']]
        while True:
            try:
                w_desc[item['description'][n]] = item['description'][n + 2]
                n = n + 6
            except:
                break
        item['description'] = w_desc
        return item


class DataBasePipeline:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.mongo_base = self.client.leroy_photos

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

    def __del__(self):
        self.client.close()


class LeroyPhotoline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img, meta=item)
                except Exception as e:
                    print(e)

    def file_path(self, request, response=None, info=None):
        media_dir = os.path.basename(request.meta['name'])
        media_name = os.path.basename(urlparse(request.url).path)
        dir = '/full/%s/%s' % (media_dir, media_name)
        return dir

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item
