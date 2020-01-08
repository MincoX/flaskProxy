import logging
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

import settings
from celery_app import celery_app
from models import Session, Proxy
from utils.proxy_check import check_proxy

logger = logging.getLogger()
logger.setLevel('DEBUG')


class ProxyTest:
    def __init__(self):
        self.queue = Queue()
        self.pool = ThreadPoolExecutor(max_workers=6)

    # 检查当前一个代理 ip 的可用性
    def __check_one_proxy(self):
        session = Session()

        # 从队列中获取代理 ip，进行检查
        proxy = self.queue.get()

        # 检查代理的可用性
        proxy = check_proxy(proxy)

        # 如果代理不可用，就让代理分数减 1
        if proxy.speed == -1:

            proxy.score['power'] += 1
            proxy.score['score'] -= proxy.score['power']
            session.add(proxy)

            logger.debug('decrease {}:{} score from {} to {}'.format(
                proxy.ip, proxy.port, proxy.score['score'] + proxy.score['power'], proxy.score['score']
            ))

            # 如果分数已经为 0 了，直接删除
            if proxy.score['score'] <= 0:
                session.delete(session.query(Proxy).filter(Proxy.ip == proxy.ip).first())
                logger.info(f'delete: {proxy.ip}:{proxy.port} score 0')
        else:
            proxy.score['power'] = 0
            if not proxy.score['score'] == settings.MAX_SCORE:
                # 如果代理可用就将该代理的分数增加到最大
                proxy.score['score'] = settings.MAX_SCORE
                logger.info(f'update: {proxy.ip}:{proxy.port} score {settings.MAX_SCORE}')

        session.commit()
        session.close()

        # 当检测逻辑检查完代理 ip 的可用性后， 调用队列的 task_done 方法, 表示一个检测任务已经完成
        self.queue.task_done()

    def run(self):
        # 从数据库获取所有的代理 ip
        session = Session()
        proxies = session.query(Proxy).all()
        session.close()

        for proxy in proxies:
            # 将待检测的 ip，添加到队列中去
            self.queue.put(proxy)

        # 开启指定个数的协程，来处理代理 ip 的检测
        for i in range(8):
            # 将检测任务存放到协程池中，
            # 使用回调函数的方式让每一个协程死循环的从队列中取出待检测的 ip，放入到协程池中
            self.pool.submit(self.__check_one_proxy).add_done_callback(self.__check_callback)

        # 让当前的线程等待队列任务的完成
        self.queue.join()

    def __check_callback(self, temp):
        """
        回调函数，让每一个协程死循环的从队列中取出待检测的代理 ip，并进行执行
        :param temp:
        :return:
        """
        self.pool.submit(self.__check_one_proxy).add_done_callback(self.__check_callback)

    @classmethod
    def start(cls):
        """
        使用 schedule 定时
        类方法，方便程序组合提供统一入口
        :return:
        """
        session = Session()
        count = session.query(Proxy).count()
        session.close()

        logger.info(f'schedule_check start! | count:{count}')
        proxy_tester = cls()
        proxy_tester.run()


@celery_app.task
def schedule_check():
    ProxyTest.start()


if __name__ == '__main__':
    ProxyTest.start()
