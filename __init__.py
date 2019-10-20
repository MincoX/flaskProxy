# from __future__ import absolute_import
from celery import Celery

# 创建celery应用对象
celery_app = Celery("async")

# 导入celery的配置信息
celery_app.config_from_object("Proxy_Server.file_celery.celery_settings")



