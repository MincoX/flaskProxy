# from __future__ import absolute_import
from celery.schedules import crontab

broker_url = "redis://127.0.0.1:6379/1"  # 使用redis存储任务队列
result_backend = "redis://127.0.0.1:6379/2"  # 使用redis存储结果

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = "Asia/Shanghai"  # 时区设置
worker_hijack_root_logger = False  # celery 默认开启自己的日志，可关闭自定义日志，不关闭自定义日志输出为空
result_expires = 60 * 60 * 24  # 存储结果过期时间（默认1天）

# 导入任务所在文件
imports = [
    "Proxy_Server.file_celery.schedule_spider",  # 定时爬虫
    "Proxy_Server.file_celery.schedule_check",  # 定时检测
]

# 需要执行任务的配置
beat_schedule = {

    'spider': {
        'task': 'Proxy_Server.file_celery.schedule_spider.schedule_spider',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': (),
    },

    'check': {
        'task': 'Proxy_Server.file_celery.schedule_check.schedule_check',
        'schedule': crontab(minute=0, hour='*/3'),
        'args': (),
    },

}
