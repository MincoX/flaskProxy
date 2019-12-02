import os
import sys
import redis

BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'Proxy_Server'))

SECRET_KEY = 'ip_pool_flask_server'
ADMIN_NAME = 'MincoX'
ADMIN_PASSWORD = 'mincoroot'
UPLOAD_FOLDER = 'App/static/upload/'


# ################################## flask config ##################################
class Config:
    DEBUG = True

    SECRET_KEY = 'ip_pool_flask_server'

    # Redis
    REDIS_HOST = '49.232.19.51'
    REDIS_PORT = 63791

    # flask_session
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True  # 对 cookie 中的 session_id 进行签名处理
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 7  # session 有效期为: 一周; 单位秒


class Develop(Config):
    """
    开发模式的配置信息
    """
    DEBUG = True


class Product(Config):
    """
    生产环境配置信息
    """
    pass


config_map = {
    'develop': Develop,
    'product': Product
}

ADMIN_NAVIGATE = [
    {'nav': '系统概况', 'href': 'dashboard'},
    {'nav': '服务配置', 'href': 'config'},
    {'nav': '权限分配', 'href': 'permission'},
    {'nav': '留言板块', 'href': 'message'},
]

USER_NAVIGATE = [

]

# ################################## main settings ##################################

# 通用爬虫的模块即类名
PROXIES_SPIDERS = [
    # 爬虫的全类名，路径： 模块，类名
    'file_spider.spiders_proxy.XiciSpider',
    'file_spider.spiders_proxy.Ip3366Spider',
    'file_spider.spiders_proxy.KuaiSpider',
    'file_spider.spiders_proxy.Ip66Spider',
]

# 测试代理 ip 的超时时间
TEST_TIME_OUT = 6

# ip 的最高分数
MAX_SCORE = 20

# 设置爬虫运行的时间间隔， 单位为小时
RUN_SPIDERS_INTERVAL = 4

# 配置检测代理 ip, 开启的异步数量
TEST_PROXIES_ASYNC_COUNT = 6

# 配置检测代理 ip 的时间间隔, 单位小时
TEST_PROXIES_INTERVAL = 2

# 配置获取最大代理 ip 的数量， 值越小可用性越高，但是随机性差
PROXIES_MAX_COUNT = 10
# ################################## main settings ##################################
