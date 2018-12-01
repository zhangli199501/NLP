import time
import requests
import re
# import os
# import glob

from bs4 import BeautifulSoup
from lxml import etree

class BeiJingSubwaySpider:
    def __init__(self, url_name, url):
        self.url_name = url_name
        self._headers = {
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
        'baike.baidu.com',
        'Upgrade-Insecure-Requests':
        '1',
        'Referer':
        'https://baike.baidu.com',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }

        self.url = url
        
#    获取链接内容返回字符串
    def get_page_str(self):
        '''
        return: soup
        '''
        response = requests.get(self.url, headers=self._headers)
        #     response.encoding='utf-8'
        #     soup = BeautifulSoup(response.text,'lxml')
        html_str = response.content.decode()
        #     html = etree.HTML(html_str)
        return html_str
        
#    存储字符串内容到文件中
    def load_content(self, string, file_path):
        #     if not os.path.exists(file_path):
        #         os.system(r"touch {}".format(file_path))
        with open(file_path, 'w', encoding='utf8') as fi:
            fi.write(string)
        return
    
    
    
# 北京地铁各条路线链接爬去
class LineSpider(BeiJingSubwaySpider):
    
    def __init__(self, url_name, url):  # 先继承，在重构
        BeiJingSubwaySpider.__init__(self, url_name, url)  #继承父类的构造方法

#    爬取首页北京地铁各条路线链接，以字典形式返回地铁名和节点链接
    def get_line_links(self):
        html_str = BeiJingSubwaySpider.get_page_str(self)
        all_lines = set(
            re.findall('<a target=_blank href="([\w|\/|\%]+)">北京地铁(\w+)</a>',
                       html_str))
        line_links = {}
        for (link, line_name) in all_lines:
            line_links[line_name] = link
        return line_links

    
    
class StationSpider(BeiJingSubwaySpider):
    
    def __init__(self, url_name, url):  # 先继承，在重构
        BeiJingSubwaySpider.__init__(self, url_name, url)  #继承父类的构造方法

#    各条路线正则，返回站点列表
    def get_station(self):
        '''
        return : list of station
        '''
        url_str = BeiJingSubwaySpider.get_page_str(self)
        html = etree.HTML(url_str)
        if self.url_name != '1号线' and self.url_name != '16号线':
            #     车站名称所在列的位置+1，因为position是从1开始计算
            station_position = html.xpath(
                "//table/caption[contains(text(),'车站列表')]/parent::table/tr[position()=1]//text()"
            ).index('车站名称') + 1
            # 找到captions含有车站列表的表格，从表格第二行开始，定位到车站列，获取车站名
            station_list = html.xpath(
                "//table/caption[contains(text(),'车站列表')]/parent::table/tr[position()>1]/*[position()={}]//text()"
                .format(station_position))
        else:
            #         1号线的'车站列表'不属于caption，找到'车站列表'的h3，通过查找后面的第一个弟节点，获取对应站台信息
            station_position = '\n'.join(
                html.xpath(
                    "//h3[contains(text(),'车站列表')]/following::table[1]/tr[position()=1]//text()"
                )).split().index('车站名称') + 1
            station_list = html.xpath(
                "//h3[contains(text(),'车站列表')]/following::table[1]/tr[position()>1]/*[position()={}]//text()"
                .format(station_position))


#         处理'\xa0'，'\r\n'
        station_list = '\n'.join(station_list).split()
        #     处理非中文
        for i in station_list:
            if not re.findall('[\u4e00-\u9fa5]', i):
                station_list.remove(i)
        return station_list