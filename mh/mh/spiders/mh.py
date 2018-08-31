# coding:utf-8

import scrapy
import os
import urllib
import zlib
from bs4 import BeautifulSoup
import re

#目前id可以从0001一直到6900 建议按照网站目录以**01-**00 100本为一次爬取目标 后面给出了四组参考
start_id = 1001  # 4001 4001 4489 4071
end_id = 2000  # 4100 5000 6837 4071

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
        total_img = 9999  # 假定一本漫画最多9999页 5036就有1165页 不会影响zfill 但会影响clearxxxp.py
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
        #document = '/home/gzd/Documents/programming/git/clone/comicsdownloader/mh/download/'
        document = '/media/gzd/本地磁盘H/漫画/18h/'
        dir_num = ((int(url_num) - 1) // 100 * 100) + 1
        document = document + str(dir_num).zfill(4) + '_' + str(dir_num + 99).zfill(4)
        # 每部漫画的文件名以页面序号和标题命名
        title = url_num.zfill(4) + '_' + title
        comics_path = document + '/' + title

        exists = os.path.exists(document)
        # 没下载过 创建新的总文件夹
        if not exists:
            self.log('create dir: ' + document)
            os.makedirs(document)
        # 查找是否有上次没下完的目录 因为并不知道最后的总标题数 所以只能查找 不能直接os.path.exist
        os.chdir(document)
        for folder in os.listdir(document):
            if title in folder:
                comics_path = os.path.relpath(folder, start=document)  # 如有则继续下载
                break
        exists = os.path.exists(comics_path)
        # 没下载过 创建新的文件夹
        if not exists:
            self.log('create dir: ' + title)
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





