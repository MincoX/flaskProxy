import importlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from . import logger
from .. import settings
from .. import celery_app
from ..models import Session, Proxy
from utils.proxy_check import check_proxy


class RunSpider:
    def __init__(self):
        # 初始化线程池大小
        self.pool = ThreadPoolExecutor(max_workers=4)

    def get_spider_obj_from_settings(self):
        """
        从 settings 文件中获取所有的具体爬虫的路径字符串
        将字符串进行分隔，得到具体爬虫的模块路径
        为每一个具体爬虫类创建一个对象
        使用协程池将每一个具体爬虫放在协程池中，使用异步方式的执行爬虫
        :return:
        """
        for full_name in settings.PROXIES_SPIDERS:
            # 从右边以 '.' 进行分隔，maxsplit 代表只分隔一次
            module_name, class_name = full_name.rsplit('.', maxsplit=1)

            # 导入具体爬虫所在的模块
            module = importlib.import_module(module_name)

            # 获取具体爬虫中的类名
            cls = getattr(module, class_name)

            # 创建具体爬虫的类对象
            spider = cls()

            yield spider

    def __execute_one_spider_task(self, spider):
        """
        一次执行具体爬虫的任务
        :param spider:
        :return:
        """
        # 异常处理，防止一个爬虫内部出错影响其它的爬虫
        try:
            # 遍历爬虫对象的 get_proxies 方法，返回每一个 代理 ip 对象
            for proxy in spider.get_proxies():
                # 检验代理 ip 的可用性
                proxy = check_proxy(proxy)
                # 如果 speed 不为 -1 说明可用，则保存到数据库中
                if proxy.speed != -1:
                    session = Session()
                    exist = session.query(Proxy)\
                        .filter(Proxy.ip == str(proxy.ip), Proxy.port == str(proxy.port))\
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
                        logger.info(f' insert: {proxy.ip}:{proxy.port} from {proxy.origin}')
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

        except Exception as e:
            logger.error(f'scrapy error: {e}')

    def run(self):
        # 获取所有的具体爬虫对象
        spiders = self.get_spider_obj_from_settings()

        # 将每一个具体爬虫放入到协程池中，用函数引用的方式指向一次具体爬虫的任务
        for spider in spiders:
            self.pool.submit(self.__execute_one_spider_task, spider)

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
# celery worker -A Proxy_Server --loglevel=info --pool=solo
