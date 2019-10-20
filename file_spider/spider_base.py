import re

import requests
from lxml import etree

import settings
from utils.http_header import get_request_header


class Proxy:

    def __init__(
            self,
            ip, port, protocol=-1, nick_type=-1, speed=-1, area=None,
            score={'score': settings.MAX_SCORE, 'power': 0},
            disable_domain=[],
            origin=''
    ):
        self.ip = ip
        self.port = port
        # 代理 ip 支持的协议类型， http:0, https:1, http/https:2
        self.protocol = protocol
        # 代理 ip 的匿名程度， 高匿：0， 匿名：1， 透明：2
        self.nick_type = nick_type
        # speed 为 -1 代表代理 ip 不可用
        self.speed = speed
        self.area = area
        # 代理 ip 的评分
        self.score = score
        # 代理 ip 的不可用域名列表
        self.disable_domain = disable_domain
        # 代理 ip 的来源
        self.origin = origin

    # 返回字符串数据
    def __str__(self):
        return str(self.__dict__)


class BaseSpider:
    """
    通用式爬虫的基类
    三个属性：
        1. urls 是一个列表，用于存放所有的有要爬取页面的 url 地址
        2. group_xpath 是 xpath 表达式，用于保存提取每一页所有的 代理列表的 xpath 语法
        3. detail_xpath 是 xpath 表达式，用于保存提取每一页代理列表中每一个 代理 ip 的 xpath 语法
    """

    urls = []
    group_xpath = ''
    detail_xpath = {}

    def __init__(self, urls=[], group_xpath='', detail_xpath={}):
        if urls:
            self.urls = urls

        if group_xpath:
            self.group_xpath = group_xpath

        if detail_xpath:
            self.detail_xpath = detail_xpath

    def get_first_from_list(self, ls):
        """
        获取列表元素的第一个值， 不存在返回空列表， 防止爬取到的列表没有元素而报错
        :return:
        """
        return ls[0] if len(ls) != 0 else ''

    def get_page(self, url):
        """
        下载页面
        :param url:
        :return:
        """
        response = requests.get(url, headers=get_request_header())

        return response.content

    def parse_page_proxy(self, page, ori):
        """
        解析每一页中的 proxy 列表
        :param page:
        :return:
        """
        html = etree.HTML(page)
        trs = html.xpath(self.group_xpath)

        for tr in trs:
            ip = self.get_first_from_list(tr.xpath(self.detail_xpath['ip']))
            port = self.get_first_from_list(tr.xpath(self.detail_xpath['port']))
            area = self.get_first_from_list(tr.xpath(self.detail_xpath['area']))

            proxy = Proxy(ip, port, area=area, origin=ori)

            # 使用 yield 返回提取到的数据
            yield proxy

    def get_proxies(self):
        for url in self.urls:
            origin = re.match(r'.*//.*?\.(.*?)\..*', url).group(1)

            page = self.get_page(url)
            proxies = self.parse_page_proxy(page, origin)

            yield from proxies


if __name__ == '__main__':

    config = {
        'urls': [f'https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-{x}' for x in range(1, 7)],
        'group_xpath': "//*[@id='page']/table[2]/tr[position()>1]",
        'detail_xpath': {
            'ip': './td[2]/text()',
            'port': './td[3]/text()',
            'area': './td[5]/text()',
        }
    }

    spider = BaseSpider(**config)
    for item in spider.get_proxies():
        print(item)
