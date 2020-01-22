import redis
import json

from manager import MODEL
from settings import config_map

config_class = config_map.get(MODEL)


class RedisModel(object):
    def __init__(self):
        if not hasattr(RedisModel, 'pool'):
            RedisModel.create_pool()

        self._connection = redis.Redis(connection_pool=RedisModel.pool)

    @staticmethod
    def create_pool():
        RedisModel.pool = redis.ConnectionPool(
            host=config_class.REDIS_HOST,
            port=config_class.REDIS_PORT,
            password=config_class.REDIS_PWD,
            db=0
        )

    def set_data(self, key, value):
        """set data with (key, value)
        """
        return self._connection.set(key, value)

    def get_data(self, key):
        """get data by key
        """
        return self._connection.get(key)

    def del_data(self, key):
        """delete cache by key
        """
        return self._connection.delete(key)

    def push_head(self, key, value):
        """
        从头部插入列表
        """
        return self._connection.lpush(key, value)

    def push_tail(self, key, value):
        """
        从尾部插入列表
        """
        return self._connection.rpush(key, value)

    def l_len(self, key):
        """
        返回列表长度
        """
        return self._connection.llen(key)

    def r_pop(self, key):
        """
        去除列表最后一个元素
        :param key:
        :return:
        """
        return self._connection.rpop(key)

    def get_range_list(self, key, start, end):
        """
        获取指定范围列表
        """
        return self._connection.lrange(key, start, end)

    def get_index_data(self, key, index):
        """
        获取列表指定下标元素
        """
        return self._connection.lindex(key, index)

    def get_hash_data(self, key, hkey):
        """
        获取哈希表指定键的值
        :param key:
        :param hkey:
        :return:
        """

        return self._connection.hget(key, hkey)

    def get_hash_all_data(self, key):
        """
        获取哈希表全部键和值
        :param key: redis键
        :return: 字典
        """

        return self._connection.hgetall(key)

    def set_hash_data(self, key, hkey, hval):
        """
        设置哈希表指定键的值，如果key不存在则会自动创建
        :param key: redis键
        :param hkey: 字典键
        :param hval: 字典值
        :return:
        """

        return self._connection.hset(key, hkey, hval)


class RedisJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return eval(str(obj, encoding='utf-8'))
        return json.JSONEncoder.default(self, obj)
