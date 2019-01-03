import requests
import re
import time
import random

from bs4 import BeautifulSoup
from lxml import etree

class PcbSpider():
    start_url = "http://pcbbbs.com"
    headers = {
        'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding':
        'gzip, deflate',
        'Accept-Language':
        'zh-CN,zh;q=0.9',
        'Cache-Control':
        'max-age=0',
        'Connection':
        'keep-alive',
        'Cookie':
        'cy=2; cye=beijing; _lxsdk_cuid=160f2a16f7bc8-010e4a62556b3f-4323461-144000-160f2a16f7cc8; _lxsdk=160f2a16f7bc8-010e4a62556b3f-4323461-144000-160f2a16f7cc8; _hc.v=88e12e9d-a024-043e-7317-7b0a4b64d0f1.1515899155; s_ViewType=10; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk_s=160f2a16f87-325-0ce-0c9%7C%7C336',
        'Host':
        'pcbbbs.com',
        'Upgrade-Insecure-Requests':
        '1',
        'Referer':
        'http://pcbbbs.com',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }

    def __init__(self):
        return

    def url2html(self, url):
        '''
        请求url，将response解码并转化为html
        :param url:需要加载的url
        :return: html
        '''
        response = requests.get(url=url, headers=self.headers)
        html_str = response.content.decode(encoding='GBK')
        return etree.HTML(html_str)

    # / html / head / meta[1]

    def get_theme_urls(self):
        '''
        解析首页内容，获取主题连接
        :return:urls of theme
        '''
        html = self.url2html(self.start_url)
        result_urls = html.xpath('//div [@id="ct"]/div[3]/div[1]/div/div[2]/table/tr/td/div/a/@href')
        return result_urls

    def get_post_urls(self, url):
        '''
        访问主题，解析主题中的贴子链接
        :param url: link in theme
        :return: links of post
        '''
        html = self.url2html(url)
        result_urls = html.xpath('//table [@id="threadlisttableid"]/tbody/tr/td[1]/a[1]/@href')
        return result_urls

    def get_page_counts(self, url, xpath):
        '''
        根据提供的url和xpath，查找相同网页最大页面数
        :return: 该网页最大页面数
        '''
        html = self.url2html(url)
        fd_page = html.xpath(xpath+'//text()')
        page_counts = 1
        if len(fd_page)>1:
            page_counts = int(''.join(re.findall('\d',fd_page[-2])))
        return page_counts

    def post_page_counts(self, url):
        '''
        查找theme页面的页数，即含有post的页数
        '''
        return self.get_page_counts(url,xpath='//*[@id="fd_page_top"]/div')

    def modify_page_url(self, url):
        '''
        判断链接后面是否有接'&page='，如果有则去掉
        '''
        if '&page=' in url:
            return url[0:url.index('&page=')]
        return url

    def get_more_post_urls(self, url, start_n=1, end_n=10, find_all=False):
        '''
        :param url:
        :param start_n: 起始页数
        :param end_n: 终止页数
        :param find_all: 是否查找全部帖子
        :return:
        '''
        result_urls = []
        page_counts = self.post_page_counts(url)
        if find_all:
            start_n,end_n = 1,page_counts
        elif end_n>page_counts:
            end_n = page_counts
        #   调整url输入
        url = self.modify_page_url(url)+'&page={}'
        for idx in range(start_n, end_n+1):
            result_urls+=self.get_post_urls(url.format(idx))
        return result_urls

    def reply_page_counts(self, url):
        '''
        回帖的最大页数
        '''
        return self.get_page_counts(url,xpath='//*[@id="pgt"]/div/div')

    def get_post_content(self, url):
        '''
        使用BeautifulSoup解析网站内容，与用户评论给出的链接
        :param url:
        :return:
            texts:用户返回文本
            links:链接
        '''
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text,'lxml')
        content = soup.find_all(class_='pl bm')[0]

        reply_urls = []
        reply_texts = ''
        for entry in content.find_all('a'):
            # 如果链接与文本一致，认为是评论中提供的链接
            href = entry.get('href')
            text = entry.get_text()
            if href==text and 'http://www.pcbbbs.com/' in href:
                reply_urls.append(href)

        for entry in content.find_all('td'):
            reply_texts += entry.get_text()

        return reply_texts,reply_urls

    def get_more_post_content(self, url, start_n=1, end_n=2, find_all=False):
        '''
        在帖子中翻页获取内容
        '''
        reply_texts = ''
        reply_urls = []
        page_counts = self.reply_page_counts(url)
        if find_all:
            start_n,end_n = 1,page_counts
        elif end_n>page_counts:
            end_n = page_counts
        #   调整url输入
        url = self.modify_page_url(url)+'&page={}'

        for idx in range(start_n, end_n+1):
            time.sleep(random.random())
            texts, urls = self.get_post_content(url.format(idx))
            reply_texts+=texts
            reply_urls+=urls
        return reply_texts,reply_urls
