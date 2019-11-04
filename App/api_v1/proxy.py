import json

from flask import request

import settings
from utils import logger
from models import protocol_map, nick_type_map, Proxy
from utils.tools import object_to_dict
from utils.api_service import ApiService, permission_api_service
from utils.proxy_check import check_proxy


# @ApiService
@permission_api_service(perms=['base'])
def get_proxies(service, limit=5):
    """
    获取高性能的代理展示于首页
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

    def get_speed_map(sd):
        if int(sd) == -1:
            return '不可用'
        if 0 < int(sd) <= 1:
            return '极快'
        elif 1 < int(sd) <= 3:
            return '优等'
        elif 3 < int(sd) <= 6:
            return '良好'
        else:
            return '较慢'

    for pro in res['proxies']:
        pro['area'] = '未知' if pro['area'].startswith('\n') else pro['area']
        pro['protocol'] = protocol_map[pro['protocol']]
        pro['nick_type'] = nick_type_map[pro['nick_type']]
        pro['speed'] = get_speed_map(pro['speed'])

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base'])
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

    proxy.area = res['area']
    proxy.speed = res['speed']
    proxy.origin = res['origin']
    proxy.protocol = res['protocol']
    proxy.nick_type = res['nick_type']
    session.commit()

    def get_speed_map(sd):
        if int(sd) == -1:
            return '不可用'
        if 0 < int(sd) <= 1:
            return '极快'
        elif 1 < int(sd) <= 3:
            return '优等'
        elif 3 < int(sd) <= 6:
            return '良好'
        else:
            return '较慢'

    res = {
        'status': 1,
        'ip': res['ip'],
        'port': res['port'],
        'origin': res['origin'],
        'area': '未知' if res['area'].startswith('\n') else res['area'],
        'protocol': protocol_map[res['protocol']],
        'nick_type': nick_type_map[res['nick_type']],
        'speed': get_speed_map(res['speed'])
    }

    return json.dumps(res)
