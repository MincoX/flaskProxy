# from __future__ import absolute_import
from celery.schedules import crontab

broker_url = "redis://47.102.134.101:6379/1"  # 使用redis存储任务队列
result_backend = "redis://47.102.134.101:6379/2"  # 使用redis存储结果

# broker_url = "redis://127.0.0.1:6379/1"  # 使用redis存储任务队列
# result_backend = "redis://127.0.0.1:6379/2"  # 使用redis存储结果

# 存储的结果被删除的时间（秒数，或者一个 timedelta 对象）
result_expires = 60 * 60 * 24
# 单个任务的运行时间限制，否则会被杀死（单位为：秒，windows 下无效）
task_time_limit = 60 * 60 * 3

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = "Asia/Shanghai"  # 时区设置
worker_hijack_root_logger = False  # celery 默认开启自己的日志，可关闭自定义日志，不关闭自定义日志输出为空

# 导入任务所在文件
imports = [
    "file_celery.schedule_spider",  # 定时爬虫
    "file_celery.schedule_check",  # 定时检测
    "file_celery.async_tasks",  # 异步任务
    "file_celery.study",  # 异步任务
]

# 需要执行任务的配置
beat_schedule = {

    'spider': {
        'task': 'file_celery.schedule_spider.schedule_spider',
        'schedule': crontab(minute=0, hour='*/4'),
        'args': (),
    },

    'check': {
        'task': 'file_celery.schedule_check.schedule_check',
        'schedule': crontab(minute=0, hour='*/6'),
        'args': (),
    },

    # 'test': {
    #     'task': 'file_celery.study.test',
    #     'schedule': crontab(minute='*/1'),
    #     'args': (),
    # },

}
