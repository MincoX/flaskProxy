import json

from flask_login import current_user

import settings
from models import Admin, Proxy
from utils.tools import object_to_dict
from utils.api_service import ApiService


@ApiService
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


@ApiService
def get_proxy_info(service):
    """
    获取当前数据库中的代理信息
    :param service:
    :return:
    """
    # TODO 所有代理数量，
    #  可用代理数量，
    #  分数阀值，
    #  低于阀值的数量
    pass


@ApiService
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


@ApiService
def get_charts(service):
    """
    获取近期爬虫曲线图
    :param service:
    :return:
    """
    return ''


@ApiService
def get_proxies(service):
    """
    获取高性能的代理展示与首页
    :param service:
    :return:
    """
    session = service.session
    proxies = session.query(Proxy).all()

    res = [object_to_dict(proxy) for proxy in proxies]

    return json.dumps(res)


if __name__ == '__main__':
    a = get_navigate()
