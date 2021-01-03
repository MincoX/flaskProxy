import redis

from flask import Flask
from flask_session import Session
from flask_wtf import CSRFProtect
from flask_cors import *  # 跨域包
from flask_login import LoginManager
from flask_socketio import SocketIO

from settings import config_map

redis_store = None
login_manager = None
socket_io = None


def create_app(config_name):
    """
    创建 app 对象
    :return:
    """

    app = Flask(__name__)

    config_class = config_map.get(config_name)
    app.config.from_object(config_class)

    global login_manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.refresh_view = 'login'

    # 响应保留 json 格式
    app.config['JSON_AS_ASCII'] = False

    # 设置所有的视图函数允许跨域请求
    CORS(app, supports_credentials=True)
    # CSRFProtect(app)

    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)

    # 利用 flask-session 将 session 数据保存到 redis 中
    app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 2  # 键有效期单位秒
    session = Session()
    session.init_app(app)

    # 配置 qq 邮箱
    app.config['MAIL_SERVER'] = 'smtp.qq.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USERNAME'] = '903444601@qq.com'
    app.config['MAIL_PASSWORD'] = 'fchqhwiuotipbbac'

    # 放在此刻导入是为了解决循环导入
    from App.api_v1 import api_v1_app
    app.register_blueprint(api_v1_app)

    global socket_io
    socket_io = SocketIO(cors_allowed_origins='*')
    socket_io.init_app(app)

    return app, socket_io
