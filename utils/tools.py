import re
import time
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


def calculate_time_countdown(end):
    """
    计算两个时间差，返回时间倒计时
    :param end:
    :return:
    """
    start = datetime.now()
    end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    start = time.mktime(start.timetuple()) * 1000 + start.microsecond / 1000
    end = time.mktime(end.timetuple()) * 1000 + end.microsecond / 1000

    total_seconds = (end - start) / 1000
    hours = int(total_seconds / 3600)
    days = int(hours / 24)
    minutes = int((total_seconds / 60) % 60)
    seconds = int(total_seconds % 60)

    return total_seconds, days, hours, minutes, seconds


def filter_tags(htmlstr):
    """
    去除富文本框中的标签
    :param htmlstr:
    :return:
    """
    # 先过滤CDATA
    re_cdata = re.compile('//<!\[CDATA\[[^>]*//\]\]>', re.I)  # 匹配CDATA
    re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)  # Script
    re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
    re_br = re.compile('<br\s*?/?>')  # 处理换行
    re_h = re.compile('</?\w+[^>]*>')  # HTML标签
    re_comment = re.compile('<!--[^>]*-->')  # HTML注释
    s = re_cdata.sub('', htmlstr)  # 去掉CDATA
    s = re_script.sub('', s)  # 去掉SCRIPT
    s = re_style.sub('', s)  # 去掉style
    s = re_br.sub('\n', s)  # 将br转换为换行
    s = re_h.sub('', s)  # 去掉HTML 标签
    s = re_comment.sub('', s)  # 去掉HTML注释
    # 去掉多余的空行
    blank_line = re.compile('\n+')
    s = blank_line.sub('\n', s)

    return s
