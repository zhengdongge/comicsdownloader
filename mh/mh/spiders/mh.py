# coding:utf-8

import scrapy
import os
import urllib
import zlib
from bs4 import BeautifulSoup
import re
import json


class Comics(scrapy.Spider):
    name = "mh"

    def start_requests(self):
        #urls = ['http://18h.mm-cg.com/18H_4470.html']
        for url_num in range(4000, 4001):
            url = 'http://18h.mm-cg.com/18H_' + str(url_num) + '.html'
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # 请求返回的html源码
        content = response.body;
        if not content:
            self.log('parse body error.')
            return

        # 用BeautifulSoup库进行节点的解析
        soup = BeautifulSoup(content, "html5lib")

        # 漫画标题
        title = soup.title.string[10:]
        jsarray = soup.find_all("script", {"language": "javascript"})
        pattern = re.compile(r'(Large\_cgurl\[1\]\s\=\s\")'
                             r'(http\:\/\/\w*\.\w*\.\w*\/file\/)'
                             r'([0-9]*)'
                             r'(\/)'
                             r'([0-9]*\_)'
                             r'([0-9]*\.jpg)'
                             r'(\")'
                             )
        for script in jsarray:
            match = pattern.search(str(script), re.I | re.U)
            if match is not None:
                #url1 = pattern.search(str(script), re.I | re.U).group(1)
                url2 = pattern.search(str(script), re.I | re.U).group(2)
                url3 = pattern.search(str(script), re.I | re.U).group(3)
                url4 = pattern.search(str(script), re.I | re.U).group(4)
                url5 = pattern.search(str(script), re.I | re.U).group(5)
        total_img = 300
        for img_mum in range(1,total_img):
            img_url = url2 + url3 + url4 + url5 + str(img_mum).zfill(3) + '.jpg'
            self.log(img_url)
            self.save_img(str(img_mum).zfill(3), title, img_url)


    def save_img(self, img_mun, title, img_url):
        # 将图片保存到本地
        self.log('saving pic: ' + img_url)

        # 保存漫画的文件夹
        document = './download'

        # 每部漫画的文件名以标题命名
        comics_path = document + '/' + title
        exists = os.path.exists(comics_path)
        if not exists:
            self.log('create document: ' + title)
            os.makedirs(comics_path)

        # 每张图片以页数命名
        pic_name = comics_path + '/' + img_mun + '.jpg'

        # 检查图片是否已经下载到本地，若存在则不再重新下载
        exists = os.path.exists(pic_name)
        if exists:
            self.log('pic exists: ' + pic_name)
            return

        try:
            user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
            headers = {'User-Agent': user_agent}

            req = urllib.request.Request(img_url, headers=headers)
            response = urllib.request.urlopen(req, timeout=30)

            # 请求返回到的数据
            data = response.read()

            # 若返回数据为压缩数据需要先进行解压
            if response.info().get('Content-Encoding') == 'gzip':
                data = zlib.decompress(data, 16 + zlib.MAX_WBITS)

            # 图片保存到本地
            fp = open(pic_name, "wb")
            fp.write(data)
            fp.close

            self.log('save image finished:' + pic_name)

        # urllib.request.urlretrieve(img_url, pic_name)
        except Exception as e:
            self.log('save image error.')
            self.log(e)





