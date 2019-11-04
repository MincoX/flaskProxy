import json
from datetime import datetime, timedelta

from flask import request
from flask_login import current_user
from sqlalchemy import cast, DATE, func, and_

import settings
from utils import logger
from models import Admin, Proxy
from utils.tools import object_to_dict, hour_range
from utils.api_service import ApiService, permission_api_service


# @ApiService
@permission_api_service(perms=['base', 'sess', 'ppp', '12546'])
def get_account_info(service):
    """
    获取当前账户信息
    :param service:
    :return:
    """
    session = service.session
    acc = session.query(Admin).get(current_user.id)
    res_dict = object_to_dict(acc)

    return res_dict


# @ApiService
@permission_api_service(perms=['base'])
def get_store_info(service):
    """
    获取当前数据库中的代理信息
    :param service:
    :return:
    """
    # TODO 所有代理数量，
    #  可用代理数量，
    #  分数阀值，
    #  低于阀值的数量
    session = service.session
    proxies = session.query(Proxy)
    active_count = proxies.filter(Proxy.speed != -1).count()
    total_count = proxies.count()
    disable_count = proxies.filter(Proxy.speed == -1).count()

    res = {
        'status': 1,
        'store_info': {'active_count': active_count, 'total_count': total_count, 'disable_count': disable_count},
    }

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base'])
def get_navigate(service):
    """
    获取首页的左侧导航栏
    :param service:
    :return:
    """
    if current_user.__tablename__ == 'admin':
        res = settings.ADMIN_NAVIGATE

    else:
        res = settings.USER_NAVIGATE

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base'])
def get_line_chart(service):
    """
    获取近期爬虫曲线图
    :param service:
    :return:
    """
    session = service.session

    lt = session.query(Proxy).order_by(Proxy.create_time.desc()).first().create_time
    bt = lt + timedelta(days=-1)
    label = hour_range(bt.strftime("%Y-%m-%d %H"), lt.strftime("%Y-%m-%d %H"))[::3]
    label = [per + ':00' for per in label]
    relabel = label[1:] + [(lt + timedelta(hours=1)).strftime("%Y-%m-%d %H") + ':00']

    def get_count(l, r, n):
        return session.query(Proxy).filter(Proxy.create_time.between(l, r), Proxy.origin == n).count()

    ip66 = map(get_count, label, relabel, ['66ip'] * len(label))
    kuaidaili = map(get_count, label, relabel, ['kuaidaili'] * len(label))
    ip3366 = map(get_count, label, relabel, ['ip3366'] * len(label))
    xicidaili = map(get_count, label, relabel, ['xicidaili'] * len(label))

    res = {
        'status': 1,
        'label': [l[5:] for l in label],
        'ip66': list(ip66),
        'kuaidaili': list(kuaidaili),
        'ip3366': list(ip3366),
        'xicidaili': list(xicidaili),
    }

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base'])
def get_total_active_scale(ser):
    """
    获取活跃量和总量的比例
    :param ser:
    :return:
    """
    session = ser.session

    proxies = session.query(Proxy).all()

    scale = {
        '66ip': f"{len([item for item in proxies if item.origin == '66ip' and item.speed != -1])} / {len([item for item in proxies if item.origin == '66ip'])}",
        '66ip_scale': f'{round(len([item for item in proxies if item.origin == "66ip" and item.speed != -1]) / len([item for item in proxies if item.origin == "66ip"]) * 100, 1)}%',
        'kuaidaili': f"{len([item for item in proxies if item.origin == 'kuaidaili' and item.speed != -1])} / {len([item for item in proxies if item.origin == 'kuaidaili'])}",
        'kuaidaili_scale': f'{round(len([item for item in proxies if item.origin == "kuaidaili" and item.speed != -1]) / len([item for item in proxies if item.origin == "kuaidaili"]) * 100, 1)}%',
        'ip3366': f"{len([item for item in proxies if item.origin == 'ip3366' and item.speed != -1])} / {len([item for item in proxies if item.origin == 'ip3366'])}",
        'ip3366_scale': f'{round(len([item for item in proxies if item.origin == "ip3366" and item.speed != -1]) / len([item for item in proxies if item.origin == "ip3366"]) * 100, 1)}%',
        'xici': f'{len([item for item in proxies if item.origin == "xicidaili" and item.speed != -1])} / {len([item for item in proxies if item.origin == "xicidaili"])}',
        'xici_scale': f'{round(len([item for item in proxies if item.origin == "xicidaili" and item.speed != -1]) / len([item for item in proxies if item.origin == "xicidaili"]) * 100, 1)}%'
    }

    res = {
        'status': 1,
        'scale': scale
    }

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base'])
def get_pie_chart(ser):
    """
    获取饼状图数据
    :return:
    """
    session = ser.session
    grouped = session.query(Proxy.origin, func.count(Proxy.id)).group_by(Proxy.origin).all()
    label = [i[0] for i in grouped]
    data = [i[1] for i in grouped]
    num = sum(data)

    res = {
        'status': 1,
        'label': label,
        'data': data,
        'scale': [
            round((data[i] / num) * 100, 2) for i in range(len(data))
        ],
        'grouped': grouped
    }

    return json.dumps(res)


if __name__ == '__main__':
    b = get_line_chart()
    print(b)
    # a = map(test, la, rela)
    # print(list(a))
