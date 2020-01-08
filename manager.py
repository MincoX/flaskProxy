import datetime
from threading import Lock
from flask_socketio import disconnect

from App import create_app
from file_celery import async_tasks

app, socket_io = create_app('develop')

_thread = None
lock = Lock()


def ack():
    print('message was received!')


@socket_io.on('connect', namespace='/conn_logging')
def connect():
    """
    请求连接
    :return:
    """
    global _thread
    socket_io.emit('message', {'data': "service connected!"}, namespace='/conn_logging', callback=ack)
    with lock:
        if _thread is None:
            _thread = socket_io.start_background_task(target=background_thread)


@socket_io.on('disconnect_request', namespace='/conn_logging')
def disconnect_request():
    """
    断开连接请求
    :return:
    """
    print('client disconnected request')
    disconnect()


@socket_io.on("recv", namespace="/conn_logging")
def recv(msg):
    """
    服务器端负责接受消息
    :param msg:
    :return:
    """
    print(f'收到消息： {msg}')


# def background_thread():
#     with open('logs/main.log', "r") as f:
#
#         while True:
#             socket_io.sleep(3)
#             # print(f'发送异步任务')
#             # async_tasks.add.delay(1, 2)
#
#             for line in f.readlines():
#                 socket_io.emit('message', {'data': line}, namespace='/conn_logging')


def background_thread():
    while True:
        current_datetime = str(datetime.datetime.now())
        current_datetime = "datetime is : " + current_datetime

        socket_io.emit("message", {"data": current_datetime}, namespace='/conn_logging')
        # 发送异步任务
        async_tasks.add.delay(1, 2)

        socket_io.sleep(10)


socket_io.run(app)
