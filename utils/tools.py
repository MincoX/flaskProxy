from datetime import datetime, timedelta

from utils import logger
from sqlalchemy.orm import class_mapper


def object_to_dict(obj):
    """
    以字典的形式返回数据模型对象的属性
    :param obj:
    :return:
    """

    def parse(o, c):
        r = getattr(o, c)

        if isinstance(r, datetime):
            return r.strftime('%Y-%m-%d %H:%M:%S')

        return r

    columns = [c.key for c in class_mapper(obj.__class__).columns]
    data = {c: parse(obj, c) for c in columns}

    return data


def object_to_list(obj):
    """
    以列表的形式返回数据模型对象的属性
    :param obj:
    :return:
    """

    def parse(o, c):
        r = getattr(o, c)

        if isinstance(r, datetime):
            return r.strftime('%Y-%m-%d %H:%M:%S')

        return r

    columns = [c.key for c in class_mapper(obj.__class__).columns]
    data = [parse(obj, c) for c in columns]

    return data


def hour_range(
        start_date=datetime.today().strftime("%Y-%m-%d") + ' 00',
        end_date=(datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d") + ' 00'
):
    """
    获取时间段中的每个整点时间刻，返回列表
    :param start_date:
    :param end_date:
    :return:
    """
    hours = []
    hour = datetime.strptime(start_date, "%Y-%m-%d %H")
    date = start_date[:]
    while date <= end_date:
        hours.append(date)
        hour = hour + timedelta(hours=1)
        date = hour.strftime("%Y-%m-%d %H")

    return hours
