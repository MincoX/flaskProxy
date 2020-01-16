import random
import time

from file_spider.spider_base import BaseSpider


class XiciSpider(BaseSpider):
    """
    实现西刺代理的爬取
    """
    urls = [f'https://www.xicidaili.com/nn/{x}' for x in range(1, 10)]

    group_xpath = "//*[@id='ip_list']/tr[position()>1]"
    detail_xpath = {
        'ip': './td[2]/text()',
        'port': './td[3]/text()',
        'area': './td[4]/text()',
    }


class Ip3366Spider(BaseSpider):
    """
    实现 Ip3366 代理的爬取
    """
    urls = [f'http://www.ip3366.net/free/?stype={x}&page={y}' for x in range(1, 3) for y in range(1, 8)]

    group_xpath = "//*[@id='list']/table/tbody/tr"

    detail_xpath = {
        'ip': './td[1]/text()',
        'port': './td[2]/text()',
        'area': './td[5]/text()',
    }


class KuaiSpider(BaseSpider):
    """
    实现 快代理 ip 网站的爬虫
    """
    urls = [f'https://www.kuaidaili.com/free/inha/{x}/' for x in range(1, 6)]

    group_xpath = "//*[@id='list']/table/tbody/tr"

    detail_xpath = {
        'ip': './td[1]/text()',
        'port': './td[2]/text()',
        'area': './td[5]/text()',
    }

    # 快代理网站做了反爬手段， 当两次页面访问的时间间隔太短时就会被发现
    # 此时重写父类爬取的方法，在两次请求页面之间随机等待 1 到 3 秒
    def get_page_from_url(self, url):
        # 随机等待 1 到 3 秒
        time.sleep(random.uniform(1, 3))

        return super().get_page(url)


class Ip66Spider(BaseSpider):
    """
    http://www.66ip.cn/1.html
    实现 66ip 网站代理 ip 的爬取
    """
    urls = [f'http://www.66ip.cn/{x}.html' for x in range(1, 20)]

    group_xpath = "//*[@id='main']/div/div[1]/table/tr[position()>1]"

    detail_xpath = {
        'ip': './td[1]/text()',
        'port': './td[2]/text()',
        'area': './td[3]/text()',
    }


if __name__ == '__main__':

    config = {
        'urls': [f'https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-{x}' for x in range(1, 6)],
        'group_xpath': "//*[@id='page']/table[2]/tr[position()>1]",
        'detail_xpath': {
            'ip': './td[2]/text()',
            'port': './td[3]/text()',
            'area': './td[5]/text()',
        }
    }

    spider = Ip66Spider()
    for item in spider.get_proxies():
        print(item)
