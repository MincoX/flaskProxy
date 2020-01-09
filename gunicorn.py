# gunicorn.py
import logging
import logging.handlers
from logging.handlers import WatchedFileHandler
import os
import multiprocessing

bind = '0.0.0.0:9999'  # 绑定ip和端口号
backlog = 512  # 监听队列
chdir = '/usr/src/Proxy_Server'  # gunicorn要切换到的目的工作目录
timeout = 30  # 超时
worker_class = 'gevent'  # 使用gevent模式，还可以使用sync 模式，默认的是sync模式
daemon = 'false'  # 守护进程,将进程交给supervisor管理

workers = multiprocessing.cpu_count() * 2 + 1  # 进程数
threads = 2  # 指定每个进程开启的线程数
loglevel = 'debug'  # 日志级别，这个日志级别指的是错误日志的级别，而访问日志的级别无法设置
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'  # 设置 gunicorn 访问日志格式，错误日志无法设置

"""
其每个选项的含义如下：
h          remote address
l          '-'
u          currently '-', may be user name in future releases
t          date of the request
r          status line (e.g. ``GET / HTTP/1.1``)
s          status
b          response length or '-'
f          referer
a          user agent
T          request time in seconds
D          request time in microseconds
L          request time in decimal seconds
p          process ID
"""
access_log = "/usr/src/Proxy_Server/logs/gunicorn_access.log"  # 访问日志文件
error_log = "/usr/src/Proxy_Server/logs/gunicorn_error.log"  # 错误日志文件
