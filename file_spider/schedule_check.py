"""
定时使用异步的方式从数据库中检测每一个代理 ip 的性能
1.  从数据库中读取所有的代理 ip, 进行检测
    如果代理 ip 不可用就将其分数 -1， 直到分数为 0， 将其进行删除
    如果可用就将其分数恢复到最大
2.  使用异步的方式提高检测速度
    2.1 把要检测的 ip 放入队列中（因为当数据库中待检测的代理 ip 数量太多时，开启多个协程会降低性能）
    2.2 从队列中获取代理 ip，通过异步回调，使用死循环不断执行这个方法
    2.3 开启多个异步任务来处理代理 ip 的检测
3.  使用定时任务，定时的开启检测任务
    3.1 定义类方法 start, 用于启动检测模块
    3.2 在 start 方法中创建类对象， 调用 run 方法， 定时执行 run 方法
"""
from gevent import monkey
from gevent.pool import Pool

monkey.patch_all()

import time
import schedule
from queue import Queue

import settings
from utils import logger
from models import Session, Proxy
from utils.proxy_check import check_proxy


# 直接使用协程池的方法会带来问题，因为数据库中有多个待检测的代理 ip，
# 如果每遍历每一个代理 ip，都开启一个协程任务放到协程池中，那么池中将会有很多任务，这样也是影响效率的
# 解决办法：将待检测的代理 ip 存放到队列中，指定开启协程的个数从队列中取出代理 ip，进行检验


class ProxyCheck:

    def __init__(self):
        self.queue = Queue()
        self.coroutine_pool = Pool()

    # 检查当前一个代理 ip 的可用性
    def __check_one_proxy(self):
        session = Session()

        # 从队列中获取代理 ip，进行检查
        proxy = self.queue.get()

        # 2.2 检查代理的可用性
        proxy = check_proxy(proxy)

        # 2.3 如果代理不可用，就让代理分数减 1
        if proxy.speed == -1:

            proxy.score['power'] += 1
            proxy.score['score'] -= proxy.score['power']
            session.add(proxy)

            logger.warning('decrease {}:{} score from {} to {}'.format(
                proxy.ip, proxy.port, proxy.score['score'] + proxy.score['power'], proxy.score['score']
            ))

            # 如果分数已经为 0 了，直接删除
            if proxy.score['score'] <= 0:
                session.delete(session.query(Proxy).filter(Proxy.ip == proxy.ip).first())
                logger.warning(f'delete: {proxy.ip}:{proxy.port} score 0')
        else:
            proxy.score['power'] = 0
            if not proxy.score['score'] == settings.MAX_SCORE:
                # 如果代理可用就将该代理的分数增加到最大
                proxy.score['score'] = settings.MAX_SCORE
                logger.warning(f'update: {proxy.ip}:{proxy.port} score {settings.MAX_SCORE}')

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

        proxy_tester = ProxyCheck()
        proxy_tester.run()

        schedule.every(settings.TEST_PROXIES_INTERVAL).hours.do(proxy_tester.run)
        while True:
            schedule.run_pending()
            # 每隔 5 秒就检测一下是否有定时任务要执行
            time.sleep(60)


if __name__ == '__main__':
    ProxyCheck.start()
