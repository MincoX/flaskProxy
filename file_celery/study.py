from abc import ABC
from datetime import datetime

from celery import Task

from celery_app import celery_app
from models import Session, CeleryTask, Proxy


class SaveTask(Task, ABC):

    def __init__(self):
        self.session = Session()

    def __call__(self, *args, **kwargs):
        print(f'task starting {self.name}, {self.request.id}')
        return super().__call__(*args, **kwargs)

    def on_success(self, result, task_id, args, kwargs):
        """
        成功执行的函数
        :param result:
        :param task_id:
        :param args:
        :param kwargs:
        :return:
        """
        print(f'任务成功执行， result: {result}, task_id: {task_id}, args: {args}, kwargs: {kwargs}')

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        失败执行的函数
        :param self:
        :param exc:
        :param task_id:
        :param args:
        :param kwargs:
        :param einfo:
        :return:
        """
        print('任务执行失败')


@celery_app.task(bind=True, base=SaveTask)
def test(self):
    """bind=True 绑定任务为 celery 的实例对象，可以访问实例的所有属性
    base=SaveTask, 为任务指定一个自定义的类，需要继承 Task 类
    """
    print(self.request.__dict__)

# celery -A celery_app worker -l debug -P gevent
