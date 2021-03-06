import os
import time
import datetime
#
# from utils import logger, redis_pool
# from utils.tools import calculate_time_countdown


# print('start')
class ApiService:
    def __init__(self, func=None):
        self.func = func

    def func_wrapper(self, *args, **kwargs):
        try:
            c = 3
            ret = self.func(c, *args, **kwargs)
        except:
            pass
        finally:
            pass

    def __call__(self, *args, **kwargs):
        return self.func_wrapper(*args, **kwargs)


@ApiService
def test(ser, a, b):
    print(ser, a, b)


def dec1(func):
    def wrapper():
        print('dec1 start')
        func()
        print('dec1 end')

    return wrapper


def dec2(func):
    def wrapper():
        print('dec2 start')
        func()
        print('dec2 end')

    return wrapper


@dec2
@dec1
def dec():
    print('dec start')
    print('dec end')


def get_file_list(path):
    """
    查找文件
    :param path:
    :return:
    """
    for home, dirs, files in os.walk(path):
        # print("#######dir list#######")
        # for dir in dirs:
        #     print(dir)
        # print("#######dir list#######")

        # print("#######file list#######")
        for filename in files:
            # print(filename)
            if filename.endswith('.pb'):
                fullname = os.path.join(home, filename)
                print(fullname)
        # print("#######file list#######")


if __name__ == '__main__':
    # print('debug')
    # test(1, 2)
    # dec()
    get_file_list(r'C:/Users/Minco/Desktop/人脸识别小程序')

    # redis_cli = redis_pool.RedisModel()
    # res = redis_cli.get_range_list('spider_error', 0, -1)
    # res = list(reversed([per.decode().split('||') for per in res]))
    # print(res)
    # len_spider_error = redis_cli.l_len('spider_error')
    # print(len_spider_error)
