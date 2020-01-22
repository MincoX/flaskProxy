import datetime
from threading import Lock
from flask_socketio import disconnect

from utils import logger
from App import create_app
from file_celery import async_tasks

MODEL = 'develop'

app, socket_io = create_app(MODEL)

_thread = None
lock = Lock()


def ack():
    print('message was received!')


# @socket_io.on('connect', namespace='/conn_logging')
@socket_io.on('connect')
def connect():
    """
    请求连接
    :return:
    """
    global _thread
    socket_io.emit('message', {'data': "service connected!"}, namespace='/conn_logging', callback=ack)
    logger.info(f'客户端已成功连接！')
    with lock:
        if _thread is None:
            _thread = socket_io.start_background_task(target=background_thread)


# @socket_io.on('disconnect_request', namespace='/conn_logging')
@socket_io.on('disconnect_request')
def disconnect_request():
    """
    断开连接请求
    :return:
    """
    logger.info(f'Client disconnected！')
    disconnect()


# @socket_io.on("recv", namespace="/conn_logging")
@socket_io.on("recv")
def recv(msg):
    """
    服务器端负责接受消息
    :param msg:
    :return:
    """
    logger.info(f'Recv from client： {msg}')


def background_thread():
    with open('logs/main.log', "r") as f:
        while True:
            socket_io.sleep(2)
            try:
                for line in f.readlines():
                    socket_io.emit('message', {'data': line})
            except Exception as e:
                logger.info(f'日志轮询错误: {e}')
                continue


# def background_thread():
#     while True:
#         current_datetime = str(datetime.datetime.now())
#         current_datetime = "datetime is : " + current_datetime
#
#         socket_io.emit("message", {"data": current_datetime}, namespace='/conn_logging')
#         # 发送异步任务
#         async_tasks.add.delay(1, 2)
#
#         socket_io.sleep(10)

if __name__ == '__main__':
    socket_io.run(app)
