"""
开启三个进程分别用于： 启动爬虫， 检测代理 ip， 启动 web 服务

"""

from multiprocessing import Process

from file_spider.spiders_run import RunSpider
from file_spider.schedule_check import ProxyCheck


# from manager import FlaskServer


def run():
    # 2.创建 启动爬虫 的进程，添加到列表中
    process_list.append(Process(target=RunSpider.start))
    # 3.创建 启动检测 的进程，添加到列表中
    process_list.append(Process(target=ProxyCheck.start))
    # 4.创建 启动 API 服务 的进程，添加到列表中
    # process_list.append(Process(target=FlaskServer.start))

    # 5. 遍历列表启动所有的进程
    for process in process_list:
        # 设置为守护进程
        process.daemon = True
        process.start()

    # 6. 遍历进程列表，让主进程等待子进程完成
    for process in process_list:
        process.join()


if __name__ == '__main__':
    # 1.定义一个列表，用于存储要启动的进程
    process_list = []
    run()
