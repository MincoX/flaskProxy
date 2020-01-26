import json
from datetime import datetime, timedelta

from flask import request
from sqlalchemy import cast, DATE, func, and_

import settings
from utils import logger, redis_pool
from models import Admin, Proxy, AdminLoginLog, CeleryTask
from utils.api_service import ApiService, permission_api_service
from utils.tools import object_to_dict, hour_range, calculate_time_countdown

redis_cli = redis_pool.RedisModel()


@permission_api_service(perms=['base'])
def get_log_dashboard(ser):
    """
    获取日志展示板
    :param ser:
    :return:
    """
    session = ser.session

    now_time = datetime.today().strftime('%Y-%m-%d')
    tasks = session.query(CeleryTask).filter(cast(CeleryTask.start_time, DATE) == now_time)

    spider_tasks = tasks.filter(CeleryTask.task_name == 'file_celery.schedule_spider.schedule_spider') \
        .order_by(CeleryTask.id.desc())
    spider = calculate_time_countdown(
        (spider_tasks.first().start_time + timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S')
    )

    check_tasks = tasks.filter(CeleryTask.task_name == 'file_celery.schedule_check.schedule_check') \
        .order_by(CeleryTask.id.desc())
    check = calculate_time_countdown(
        (check_tasks.first().start_time + timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S')
    )

    res = {
        'status': 1,
        'server': {
            'error_count': redis_cli.l_len('spider_error'),
            'error_info': redis_cli.get_range_list('spider_error', -1, -1).decode()
            if redis_cli.l_len('spider_error') >= 1 else ''
        },
        'spider': {
            'status': spider_tasks.first().task_status,
            'countdown': [spider[2], spider[3], spider[4]],
            'task_active': f'{spider_tasks.count()} / 6',
            'harvest': sum([task.harvest for task in spider_tasks])
        },
        'check': {
            'status': check_tasks.first().task_status,
            'countdown': [check[2], check[3], check[4]],
            'task_active': f'{check_tasks.count()} / 4',
            'harvest': sum([task.harvest for task in check_tasks])
        },
    }

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base'])
def post_login_log(ser):
    """
    获取登录日志
    :param ser:
    :return:
    """
    session = ser.session

    filter_date = request.form.get('filter_date').replace('/', '-')
    filter_date = datetime.strptime(filter_date, '%Y-%m-%d').strftime('%Y-%m-%d')
    login_logs = session.query(AdminLoginLog) \
        .filter(cast(AdminLoginLog.create_time, DATE) == filter_date) \
        .order_by(AdminLoginLog.create_time.desc()) \
        .all()

    res = {
        'status': 1,
        'login_info': [
            {
                'id': login_log.admin.id,
                'ip': login_log.ip,
                'username': login_log.admin.username,
                'log_create_time': login_log.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'account_create_time': login_log.admin.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'active': login_log.admin.active
            }
            for login_log in login_logs
        ]
    }

    return json.dumps(res)


@permission_api_service(perms=['base'])
def get_server_log(ser):
    """
    获取 redis 中的报错日志
    :param ser:
    :return:
    """

    error_list = redis_cli.get_range_list('spider_error', 0, -1)
    error_list = [per.decode().split('||') for per in error_list]

    res = {
        'status': 1,
        'error_list': error_list
    }

    return json.dumps(res)


@permission_api_service(perms=['base'])
def post_celery_task(ser):
    """
    获取 celery 任务列表
    :param ser:
    :return:
    """
    session = ser.session

    filter_date = request.form.get('filter_date').replace('/', '-')
    filter_date = datetime.strptime(filter_date, '%Y-%m-%d').strftime('%Y-%m-%d')
    tasks = session.query(CeleryTask).filter(cast(CeleryTask.end_time, DATE) == filter_date)

    res = {
        'status': 1,
        'task_list': [
            {
                'task_id': task.task_id,
                'task_name': task.task_name.split('.')[-1],
                'task_status': task.task_status,
                'start_time': task.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': task.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'times': task.times,
                'harvest': task.harvest,
            }
            for task in tasks
        ]
    }

    return json.dumps(res)
