import os
import multiprocessing

workers = 1  # 使用 socketio worker 要设置为 1
# workers = multiprocessing.cpu_count() * 2 + 1

bind = '0.0.0.0:9999'
chdir = '/usr/src/Proxy_Server'
worker_class = 'eventlet'
threads = 2  # 指定每个进程开启的线程数
worker_connections = 100

timeout = 30
daemon = 'false'  # 守护进程,将进程交给supervisor管理

loglevel = 'debug'  # 日志级别，这个日志级别指的是错误日志的级别，而访问日志的级别无法设置
access_log = "/usr/src/Proxy_Server/logs/gunicorn_access.log"  # 访问日志文件
error_log = "/usr/src/Proxy_Server/logs/gunicorn_error.log"  # 错误日志文件
