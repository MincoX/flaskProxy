from datetime import datetime

from celery import Task

from celery_app import celery_app
from models import Session, CeleryTask, Proxy


#
#
# class CallbackTask(Task):
#
#     def __init__(self):
#         self.session = Session()
#
#     def on_success(self, result, task_id, args, kwargs):
#         """
#         成功执行的函数
#         :param result:
#         :param task_id:
#         :param args:
#         :param kwargs:
#         :return:
#         """
#         print(f'result: {result}, task_id: {task_id}, args: {args}, kwargs: {kwargs}')
#
#         task = self.session.query(CeleryTask).filter(CeleryTask.task_id == task_id).first()
#         task.end_time = datetime.now()
#         task.task_status = 0
#         self.session.commit()
#         self.session.close()
#
#     def on_failure(self, exc, task_id, args, kwargs, einfo):
#         """
#         失败执行的函数
#         :param self:
#         :param exc:
#         :param task_id:
#         :param args:
#         :param kwargs:
#         :param einfo:
#         :return:
#         """
#         task = self.session.query(CeleryTask).filter(CeleryTask.task_id == task_id).first()
#         task.end_time = datetime.now()
#         task.task_status = -1
#         self.session.commit()
#         self.session.close()


@celery_app.task
def add(x, y):
    print(f'执行任务之时'.center(100, '*'))
    import time
    time.sleep(15)
    return x + y


@celery_app.task
def sc():
    print(f'发送任务之前'.center(100, '*'))
    task_id = add.delay(1, 2)
    session = Session()
    celery_task = CeleryTask(
        task_id=task_id,
        task_name='spider',
        task_status=1,
        start_time=datetime.now(),
        end_time=datetime.now(),
        times='0',
        harvest=0
    )
    session.add(celery_task)
    session.commit()
    session.close()
    print(f'发送任务之后{task_id}'.center(100, '*'))

# celery -A celery_app worker -l debug -P gevent
