# coding:utf-8

import scrapy
import os
import urllib
import zlib
from bs4 import BeautifulSoup
import re

#目前id可以从0001一直到6900 建议按照网站目录以**01-**00 100本为一次爬取目标
start_id = 5501  # 4001 4071
end_id = 5600  # 4100 4071

class Comics(scrapy.Spider):
    name = "mh"

    def start_requests(self):
        #通过两个id设定爬取的网页组
        for url_num in range(start_id, end_id + 1):
            url = 'http://18h.mm-cg.com/18H_' + str(url_num).zfill(4) + '.html'
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # 请求返回的html源码
        content = response.body;
        if not content:
            self.log('parse body error.')
            return

        # 用BeautifulSoup库进行节点的解析
        soup = BeautifulSoup(content, "html5lib")
        url_num = response.request.url[25:29]
        # 漫画标题
        title = soup.title.string[10:]
        # 获取在js图片的url
        jsarray = soup.find_all("script", {"language": "javascript"})
        # 匹配第一图片url list的正则表达式
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
            # 第一个js并不是目标
            if match is not None:
                #url1 = pattern.search(str(script), re.I | re.U).group(1)
                url2 = pattern.search(str(script), re.I | re.U).group(2)
                url3 = pattern.search(str(script), re.I | re.U).group(3)
                url4 = pattern.search(str(script), re.I | re.U).group(4)
                url5 = pattern.search(str(script), re.I | re.U).group(5)
        total_img = 600  # 假定一本漫画最多有600页
        end_img = 0
        for img_num in range(1,total_img):
            img_url = url2 + url3 + url4 + url5 + str(img_num).zfill(3) + '.jpg'
            #self.log(img_url)
            download = self.save_img(url_num, img_num, title, img_url, end_img, response)
            # 返回值为false表示已经产生404 爬完了该漫画的所有图片了
            if not download:
                end_img = img_num - 1
                self.save_img(url_num, img_num, title, img_url, end_img, response)  # 修改文件夹名
                break

    def save_img(self, url_num, img_num, title, img_url, end_img, response):
        # 将图片保存到本地
        self.log('saving pic: ' + img_url)

        # 保存漫画的文件夹
        #document = './download/'
        dir_num = (start_id // 100 * 100) + 1;
        document = '/media/gzd/本地磁盘H/漫画/18h/' + str(dir_num) + '_' + str(dir_num + 99)
        # 每部漫画的文件名以页面序号和标题命名
        title = url_num + '_' + title
        comics_path = document + '/' + title
        # 创建新的目录
        os.chdir(document)
        for folder in os.listdir(document):
            if title in folder:
                comics_path = os.path.relpath(folder, start=document)
                break
        exists = os.path.exists(comics_path)
        if not exists:
            self.log('create document: ' + title)
            os.makedirs(comics_path)
        # 创建新的log文件
        exists = os.path.exists(comics_path + '/log.txt')
        if not exists:
            fobj = open(comics_path + '/log.txt', 'a')
            fobj.write(response.request.url + '\n')  # 保存漫画页面url
            fobj.write(img_url + '\n')  # 保存漫画图库第一张照片url
            fobj.close()

        # 爬完一本漫画后且未修改过漫画文件夹名 修改文件夹名 添加页数信息
        if (end_img != 0) and (folder == title):
            comics_path_old = comics_path
            comics_path_new = comics_path + '[' + str(end_img).zfill(3) + 'p]'
            os.rename(comics_path_old, comics_path_new)
            return

        # 每张图片以页数命名
        pic_name = comics_path + '/' + str(img_num).zfill(3) + '.jpg'

        # 检查图片是否已经下载到本地，若存在则不再重新下载
        exists = os.path.exists(pic_name)
        if exists:
            self.log('pic exists: ' + pic_name)
            return True

        try:
            user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
            headers = {'User-Agent': user_agent}

            req = urllib.request.Request(img_url, headers=headers)
            response = urllib.request.urlopen(req, timeout=3)

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
            return True

        # urllib.request.urlretrieve(img_url, pic_name)
        except Exception as e:
            self.log('save image error.')
            self.log(e) #基本上是404 表示该本漫画已经爬完
            return False





