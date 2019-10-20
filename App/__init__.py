import redis

from flask import Flask
from flask_session import Session
from flask_wtf import CSRFProtect
from flask_cors import *  # 跨域包
from flask_login import LoginManager

from settings import config_map

# redis, 放在外面是为了以属性的方式将其导入到别的模块使用
# 不直接创建 redis 连接对象而是推迟到创建 app 对象时再创建 redis 对象是因为:
# 切换开发环境时, 不同的开发环境下的 redis ip:port 的配置可能不同, 所以要将创建 redis 连接对象推迟到创建 app 中执行
redis_store = None
login_manager = None


# 工厂模式
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

    # 创建 redis, 不同环境下 redis 的配置不同, 所以 redis 连接对象推迟到创建 app 对象时创建
    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)

    # 利用 flask-session 将 session 数据保存到 redis 中
    Session(app)

    # 为 app 开启 csrf 防护
    CSRFProtect(app)

    # 注册蓝图
    from App.api_v1 import api_v1_app  # 放在此刻导入是为了解决循环导入
    app.register_blueprint(api_v1_app)

    return app
