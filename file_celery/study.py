from datetime import datetime

from abc import ABC
from celery import Task

from celery_app import celery_app


class SaveTask(Task, ABC):

    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        print(f'任务开始执行, {self.request.id}, {self.name}')
        return super().__call__(*args, **kwargs)

    def on_success(self, result, task_id, args, kwargs):
        """
        任务执行成功
        :param result:
        :param task_id:
        :param args:
        :param kwargs:
        :return:
        """
        print(f'任务成功执行， result: {result}, task_id: {task_id}, args: {args}, kwargs: {kwargs}')

    def on_failure(self, exc, task_id, args, kwargs, error_info):
        """
        任务执行失败
        :param self:
        :param exc:
        :param task_id:
        :param args:
        :param kwargs:
        :param error_info:
        :return:
        """
        print(f'任务成功失败: {exc}, {task_id}, {args}, {kwargs}, {error_info}')


@celery_app.task(bind=True, base=SaveTask)
def test(self):
    """bind=True 绑定任务为 celery 的实例对象，可以访问实例的所有属性
    base=SaveTask, 为任务指定一个自定义的类，需要继承 Task 类
    """
    print(self.request.__dict__)

# celery -A celery_app beat -l info
# celery -A celery_app worker -l debug -P gevent
