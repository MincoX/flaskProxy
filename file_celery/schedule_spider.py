from gevent import monkey
from gevent.pool import Pool

monkey.patch_all()

import json
import importlib
from datetime import datetime

import settings
from utils import logger
from utils import redis_pool
from models import Session, Proxy
from celery_app import celery_app
from utils.celery_tools import SaveTask
from utils.proxy_check import check_proxy


class RunSpider:
    def __init__(self):
        self.coroutine_pool = Pool()
        self.redis_cli = redis_pool.RedisModel()

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
                        logger.info(f'insert: {proxy.ip}:{proxy.port} from {proxy.origin}!')
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
                        logger.info(f'update: {proxy.ip}:{proxy.port}, to max score successfully!')
                else:
                    logger.info(f'invalid: {proxy.ip}:{proxy.port} from {proxy.origin}')

        except Exception as e:
            logger.error(f'spider error: {e}')

            error_info = str(type(self).__name__) + ':' + str(e) + '||' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.redis_cli.push_tail('spider_error', error_info)

    def run(self):
        spiders = self.get_spider_obj_from_settings()

        for spider in spiders:
            self.coroutine_pool.apply_async(self.__execute_one_spider_task, args=(spider,))

        # 使用协程池的 join 方法，让当前线程等待协程池的任务完成
        self.coroutine_pool.join()

    @classmethod
    def start(cls):
        """
        使用 schedule 定时
        类方法，方便最后整合直接通过 类名.start() 方法去执行这个类里面的所任务
        :return:
        """
        rs = cls()
        rs.run()


@celery_app.task(bind=True, base=SaveTask)
def schedule_spider(self):
    RunSpider.start()


if __name__ == '__main__':
    RunSpider.start()
