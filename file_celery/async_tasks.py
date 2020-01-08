from celery import Task

from celery_app import celery_app


class CallbackTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        """
        成功执行的函数
        :param retval:
        :param task_id:
        :param args:
        :param kwargs:
        :return:
        """
        print(f'task_id: {task_id}, retval: {retval}, args: {args}, kwargs: {kwargs}')
        print(f'任务执行完毕， 执行回调函数： {get_res(retval)}')


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
    print("callback failure function")


@celery_app.task(base=CallbackTask)
def add(x, y):
    return x + y


def get_res(x):
    return x
