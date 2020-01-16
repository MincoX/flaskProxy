import time
from datetime import datetime

from abc import ABC
from celery import Task

from utils import logger
from models import Session, CeleryTask, Proxy


class SaveTask(Task, ABC):

    def __init__(self):
        self.session = Session()

    def __call__(self, *args, **kwargs):
        """
        任务开始之前将任务保存到任务表中
        :param args:
        :param kwargs:
        :return:
        """
        logger.info(f'{self.name} 任务开始执行!'.center(100, '*'))

        self.task = CeleryTask(
            task_id=str(self.request.id),
            task_name=str(self.name),
            task_status=1,
            harvest=self.session.query(Proxy).count()
        )
        self.session.add(self.task)
        self.session.commit()

        return super().__call__(*args, **kwargs)

    @staticmethod
    def get_time_cost(t1, t2):
        """
        获取任务的时间开销
        :param t1:
        :param t2:
        :return:
        """
        start = datetime.strptime(t1.strftime('%Y-%y-%d %H:%M:%S'), '%Y-%y-%d %H:%M:%S')
        end = datetime.strptime(t2.strftime('%Y-%y-%d %H:%M:%S'), '%Y-%y-%d %H:%M:%S')
        start = time.mktime(start.timetuple()) * 1000 + start.microsecond / 1000
        end = time.mktime(end.timetuple()) * 1000 + end.microsecond / 1000

        total_seconds = (end - start) / 1000
        hours = int(total_seconds / 3600)
        days = int(hours / 24)
        minutes = int((total_seconds / 60) % 60)
        seconds = int(total_seconds % 60)

        return f'{days} 天, {hours} 时, {minutes} 分, {seconds} 秒'

    def on_success(self, result, task_id, args, kwargs):
        """
        任务执行成功
        :param result:
        :param task_id:
        :param args:
        :param kwargs:
        :return:
        """
        # print(f'任务成功执行， result: {result}, task_id: {task_id}, args: {args}, kwargs: {kwargs}')

        self.task.end_time = datetime.now()
        self.task.task_status = '0'
        self.task.times = self.get_time_cost(self.task.start_time, self.task.end_time)
        self.task.harvest = self.session.query(Proxy).count() - self.task.harvest

        self.session.commit()
        self.session.close()

        logger.info(f'{self.name} 任务执行完成!'.center(100, '*'))

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
        # print(f'任务成功失败: {exc}, {task_id}, {args}, {kwargs}, {error_info}')

        self.task.end_time = datetime.now()
        self.task.task_status = '-1'
        self.task.times = self.get_time_cost(self.task.start_time, self.task.end_time)
        self.task.harvest = self.session.query(Proxy).count() - self.task.harvest

        self.session.commit()
        self.session.close()

        logger.info(f'{self.name} 任务执行失败!'.center(100, '*'))
