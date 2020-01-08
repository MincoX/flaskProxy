import time
import logging
import threading
import importlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import settings
from utils import logger
from celery_app import celery_app
from models import Session, Proxy
from utils.proxy_check import check_proxy


class RunSpider:

    def get_spider_obj_from_settings(self):
        """
        从 settings 文件中获取所有的具体爬虫的路径字符串
        将字符串进行分隔，得到具体爬虫的模块路径
        为每一个具体爬虫类创建一个对象
        使用协程池将每一个具体爬虫放在协程池中，使用异步方式的执行爬虫
        :return:
        """
        for full_name in settings.PROXIES_SPIDERS:
            module_name, class_name = full_name.rsplit('.', maxsplit=1)
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            spider = cls()

            yield spider

    def __execute_one_spider_task(self, spider):
        """
        一次执行具体爬虫的任务
        :param spider:
        :return:
        """
        start_time = time.time()
        logger.info(f'>>> {type(spider).__name__} 线程开始执行!')
        try:
            for proxy in spider.get_proxies():
                proxy = check_proxy(proxy)
                if proxy.speed != -1:
                    session = Session()
                    exist = session.query(Proxy) \
                        .filter(Proxy.ip == str(proxy.ip), Proxy.port == str(proxy.port)) \
                        .first()

                    if not exist:
                        obj = Proxy(
                            ip=str(proxy.ip),
                            port=str(proxy.port),
                            protocol=proxy.protocol,
                            nick_type=proxy.nick_type,
                            speed=proxy.speed,
                            area=str(proxy.area),
                            score=proxy.score,
                            disable_domain=proxy.disable_domain,
                            origin=str(proxy.origin),
                            create_time=datetime.now()
                        )
                        session.add(obj)
                        session.commit()
                        session.close()
                        logger.warning(f' insert: {proxy.ip}:{proxy.port} from {proxy.origin}')
                    else:
                        exist.score['score'] = settings.MAX_SCORE
                        exist.score['power'] = 0
                        exist.port = proxy.port
                        exist.protocol = proxy.protocol
                        exist.nick_type = proxy.nick_type
                        exist.speed = proxy.speed
                        exist.area = proxy.area
                        exist.disable_domain = proxy.disable_domain
                        exist.origin = proxy.origin
                        session.commit()
                        session.close()
                        logger.info(f' already exist {proxy.ip}:{proxy.port}, update successfully')
                else:
                    logger.debug(f' invalid {proxy.ip}:{proxy.port} from {proxy.origin}')
            end_time = time.time()
            m, s = divmod(end_time - start_time, 60)
            logger.warning(f'>>> {type(spider).__name__} 线程执行结束, 耗时 {m} 分 {s} 秒,'
                        f' 剩余线程 {threading.activeCount() - 1} 个。')

        except Exception as e:
            logger.error(f'spider: {type(spider).__name__}, error: {e}')

    def run(self):
        spiders = self.get_spider_obj_from_settings()

        with ThreadPoolExecutor(max_workers=4) as t:  # 创建一个最大容纳数量为 4 的线程池

            # 通过submit提交执行的函数到线程池中
            for spider in spiders:
                type(spider).__name__ = t.submit(self.__execute_one_spider_task, spider)

    @classmethod
    def start(cls):
        """
        使用 schedule 定时
        类方法，方便最后整合直接通过 类名.start() 方法去执行这个类里面的所任务
        :return:
        """
        # 创建当前类对象，使用当前类对象调用当前类中的 run 方法，执行所有的具体爬虫
        rs = cls()
        rs.run()


@celery_app.task
def schedule_spider():
    RunSpider.start()


if __name__ == '__main__':
    RunSpider.start()
