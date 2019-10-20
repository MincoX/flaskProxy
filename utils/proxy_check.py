"""
将爬取的代理 ip 向 'http://httpbin.org/get'/'https://httpbin.org/get' 这两个网址发送请求，检验代理 ip 的性能

"""

import time
import json
import requests

import settings
from file_spider.spider_base import Proxy
from utils.http_header import get_request_header


def __check_http_proxies(proxies, is_http=True):
    """
    检测代理 ip 的响应速度， 匿名程度， 支持的协议类型
    :param proxies:
    :param is_http:
    :return:
    """
    # 匿名程度： 高匿：0， 匿名：1， 透明：2
    nick_type = -1

    # 响应速度, 单位s（-1 代表默认不可用）
    speed = -1

    if is_http:
        test_url = 'http://httpbin.org/get'

    else:
        test_url = 'https://httpbin.org/get'

    try:
        # 获取开始时间
        start = time.time()
        # 发送请求获取响应数据
        response = requests.get(
            test_url,
            headers=get_request_header(),
            proxies=proxies,
            timeout=settings.TEST_TIME_OUT
        )
        response_text = json.loads(response.text)
        if response.ok:
            # 计算响应速度
            speed = round(time.time() - start, 2)
            # 获取匿名程度
            origin = response_text['origin']  # 获取来源 ip: origin
            proxy_connection = response_text['headers'].get('Proxy-Connection', None)

            # 如果响应的 origin 中有以 ',' 分隔的两个 ip 就是透明的代理 ip
            if ',' in origin:
                nick_type = 2

            # 如果响应的 headers 中包含 Proxy-Connection 说明是匿名代理 ip
            elif proxy_connection:
                nick_type = 1

            # 否则就是高匿代理 ip
            else:
                nick_type = 0

            return True, nick_type, speed

        return False, nick_type, speed

    except:

        return False, nick_type, speed


def check_proxy(proxy):
    """
    调用 __check_http_proxies 执行具体的检测
    得到检测后的数据，对数据进行更新
    :param proxy:
    :return:
    """
    proxies = {
        'http': f'http://{proxy.ip}:{proxy.port}',
        'https': f'https://{proxy.ip}:{proxy.port}'
    }

    # 测试代理 ip
    http, http_nick_type, http_speed = __check_http_proxies(proxies)
    https, https_nick_type, https_speed = __check_http_proxies(proxies, False)

    # 代理 IP 支持的协议类型， http：0， https: 1，http/https: 2
    if http and https:
        proxy.protocol = 2
        proxy.nick_type = http_nick_type
        proxy.speed = http_speed
    elif http:
        proxy.protocol = 0
        proxy.nick_type = http_nick_type
        proxy.speed = http_speed
    elif https:
        proxy.protocol = 1
        proxy.nick_type = https_nick_type
        proxy.speed = http_speed
    else:
        # 否则就是 http/https 均不可用，那么此代理 ip 就不可用
        proxy.protocol = -1
        proxy.nick_type = -1
        proxy.speed = -1

    return proxy


if __name__ == '__main__':
    pr = Proxy(ip='127.0.0.1', port=8888)
    print(check_proxy(pr))
