import json

from flask import request

import settings
from utils import logger
from models import Proxy
from utils.tools import object_to_dict
from utils.api_service import ApiService
from utils.proxy_check import check_proxy


@ApiService
def get_proxies(service, limit=5):
    """
    获取高性能的代理展示与首页
    :param limit:
    :param service:
    :return:
    """
    session = service.session

    proxies = session.query(Proxy).filter(Proxy.speed != -1).all()
    res = {
        'status': 1,
        'proxies': [object_to_dict(proxy) for proxy in proxies],
    }

    return json.dumps(res)


@ApiService
def post_check(service):
    """
    测试代理
    :param service:
    :return:
    """
    session = service.session

    proxy_id = request.form.get('proxyId')
    proxy = session.query(Proxy).get(proxy_id)

    proxy = check_proxy(proxy)
    res = object_to_dict(proxy)

    return json.dumps(res)
