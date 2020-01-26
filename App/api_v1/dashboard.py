import json
from datetime import datetime, timedelta

from flask import request
from flask_login import current_user
from sqlalchemy import cast, DATE, func, and_

import settings
from utils import logger
from models import Admin, Proxy, CeleryTask
from utils.api_service import ApiService, permission_api_service
from utils.tools import object_to_dict, hour_range, calculate_time_countdown


# @ApiService
@permission_api_service(perms=['base'])
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
    session = service.session

    date_today = datetime.today().strftime('%Y-%m-%d')
    proxies = session.query(Proxy)
    active_count = proxies.filter(Proxy.speed != -1).count()
    total_count = proxies.count()
    disable_count = proxies.filter(Proxy.speed == -1).count()

    tasks = session.query(CeleryTask).filter(cast(CeleryTask.start_time, DATE) == date_today)

    spider_task = tasks.filter(CeleryTask.task_name == 'file_celery.schedule_spider.schedule_spider') \
        .order_by(CeleryTask.id.desc()).first()
    spider = calculate_time_countdown(
        (spider_task.start_time + timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S')
    )

    check_task = tasks.filter(CeleryTask.task_name == 'file_celery.schedule_check.schedule_check') \
        .order_by(CeleryTask.id.desc()).first()
    check = calculate_time_countdown(
        (check_task.start_time + timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S')
    )

    res = {
        'status': 1,
        'store_info': {'active_count': active_count, 'total_count': total_count, 'disable_count': disable_count},
        'spider_countdown': [spider[2], spider[3], spider[4]],
        'check_countdown': [check[2], check[3], check[4]]
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
def post_line_chart(service):
    """
    获取近期爬虫曲线图
    :param service:
    :return:
    """
    session = service.session
    filter_date = request.form.get('filter_date').replace('/', '-')
    filter_date = datetime.strptime(filter_date, '%Y-%m-%d').strftime('%Y-%m-%d')

    if filter_date and filter_date != datetime.today().strftime('%Y-%m-%d'):
        filter_date = datetime.strptime(filter_date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        lt = filter_date + timedelta(days=1)
        bt = filter_date
    else:
        obj = session.query(Proxy).order_by(Proxy.create_time.desc()).first()

        if not obj:
            res = {
                'status': 0,
                'message': '库存为空！'
            }

            return res

        lt = obj.create_time
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
def post_total_active_scale(ser):
    """
    获取当天 活跃量 / 过期量
    :param ser:
    :return:
    """
    session = ser.session
    filter_date = request.form.get('filter_date').replace('/', '-')
    filter_date = datetime.strptime(filter_date, '%Y-%m-%d').strftime('%Y-%m-%d')

    proxies = session.query(Proxy).filter(cast(Proxy.create_time, DATE) == filter_date)

    ip66 = proxies.filter(Proxy.origin == '66ip').all()
    active_ip66 = [item for item in ip66 if item.speed != -1]

    kuaidaili = proxies.filter(Proxy.origin == 'kuaidaili').all()
    active_kuaidaili = [item for item in kuaidaili if item.speed != -1]

    ip3366 = proxies.filter(Proxy.origin == 'ip3366').all()
    active_ip3366 = [item for item in ip3366 if item.speed != -1]

    xici = proxies.filter(Proxy.origin == 'xicidaili').all()
    active_xici = [item for item in xici if item.speed != -1]

    scale = {
        '66ip': f"{len(active_ip66)}"
                f"/"
                f"{len(ip66) - len(active_ip66)}",
        '66ip_scale': f"{round(len(active_ip66) / len(ip66) * 100 if len(ip66) != 0 else 0, 1)}%",

        'kuaidaili': f"{len(active_kuaidaili)}"
                     f"/"
                     f"{len(kuaidaili) - len(active_kuaidaili)}",
        'kuaidaili_scale': f"{round(len(active_kuaidaili) / len(kuaidaili) * 100 if len(kuaidaili) != 0 else 0, 1)}%",

        'ip3366': f"{len(active_ip3366)}"
                  f"/"
                  f"{len(ip3366) - len(active_ip3366)}",
        'ip3366_scale': f"{round(len(active_ip3366) / len(ip3366) * 100 if len(ip3366) != 0 else 0, 1)}%",

        'xici': f"{len(active_xici)}"
                f"/"
                f"{len(xici) - len(active_xici)}",
        'xici_scale': f"{round(len(active_xici) / len(xici) * 100 if len(xici) != 0 else 0, 1)}%",
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
            round((data[i] / num if num != 0 else 0) * 100, 2) for i in range(len(data))
        ],
        'grouped': grouped
    }

    return json.dumps(res)


if __name__ == '__main__':
    pass
    # b = post_line_chart()
    # print(b)
    # a = map(test, la, rela)
    # print(list(a))
