from gevent import monkey
from gevent.pool import Pool

monkey.patch_all()

from queue import Queue

import settings
from utils import logger
from celery_app import celery_app
from models import Session, Proxy
from utils.celery_tools import SaveTask
from utils.proxy_check import check_proxy


class ProxyTest:

    def __init__(self):
        self.queue = Queue()
        self.coroutine_pool = Pool()

    def __check_one_proxy(self):
        session = Session()

        proxy = self.queue.get()
        proxy = check_proxy(proxy)

        if proxy.speed == -1:
            proxy.score['power'] += 1
            proxy.score['score'] -= proxy.score['power']
            session.add(proxy)

            logger.info('decrease: {}:{} score from {} to {}!'.format(
                proxy.ip, proxy.port, proxy.score['score'] + proxy.score['power'], proxy.score['score']
            ))

            if proxy.score['score'] <= 0:
                session.delete(session.query(Proxy).filter(Proxy.ip == proxy.ip).first())
                logger.warning(f'delete: {proxy.ip}:{proxy.port} score 0!')
        else:
            proxy.score['power'] = 0
            if not proxy.score['score'] == settings.MAX_SCORE:
                proxy.score['score'] = settings.MAX_SCORE
                logger.info(f'update: {proxy.ip}:{proxy.port}, to max score successfully!')

        session.commit()
        session.close()

        self.queue.task_done()

    def run(self):
        session = Session()
        proxies = session.query(Proxy).all()
        session.close()

        for proxy in proxies:
            self.queue.put(proxy)

        # 开启指定个数的协程，来处理代理 ip 的检测
        for i in range(settings.TEST_PROXIES_ASYNC_COUNT):
            # 将检测任务存放到协程池中，
            # 使用回调函数的方式让每一个协程死循环的从队列中取出待检测的 ip，放入到协程池中
            self.coroutine_pool.apply_async(self.__check_one_proxy, callback=self.__check_callback)

        # 让当前的线程等待队列任务的完成
        self.queue.join()

    def __check_callback(self, temp):
        """
        回调函数，让每一个协程死循环的从队列中取出待检测的代理 ip，并进行执行
        :param temp:
        :return:
        """
        self.coroutine_pool.apply_async(self.__check_one_proxy, callback=self.__check_callback)

    @classmethod
    def start(cls):
        """
        使用 schedule 定时
        类方法，方便程序组合提供统一入口
        :return:
        """
        proxy_tester = cls()
        proxy_tester.run()


@celery_app.task(bind=True, base=SaveTask)
def schedule_check(self):
    ProxyTest.start()


if __name__ == '__main__':
    ProxyTest.start()
