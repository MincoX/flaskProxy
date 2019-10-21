from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.orm import sessionmaker

import settings


# 创建 SQLAlchemy 的引擎对象
engine = create_engine(
    "mysql+mysqlconnector://root:root@127.0.0.1:3306/proxy_server",
    max_overflow=0,  # 超过连接池大小外最多创建的连接
    pool_size=5,  # 连接池大小
    pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
    pool_recycle=-1  # 多久之后对线程池中的线程进行一次连接的回收（重置）
)

Base = declarative_base()
Session = sessionmaker(bind=engine)


class Admin(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(128), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    @property
    def role(self):
        return 'admin'

    def __repr__(self):
        return f'{self.id}:{self.username}'


class Proxy(Base):
    __tablename__ = 'proxy'

    id = Column(Integer, primary_key=True)
    ip = Column(String(64))
    port = Column(String(64))
    # 代理 ip 支持的协议类型， http:0, https:1, http/https:2
    protocol = Column(Integer, default=-1)
    # 代理 ip 的匿名程度， 高匿：0， 匿名：1， 透明：2
    nick_type = Column(Integer, default=-1)
    # speed 为 -1 代表代理 ip 不可用
    speed = Column(Float, default=-1)
    area = Column(String(255), default='')
    score = Column(MutableDict.as_mutable(JSON), default={'score': settings.MAX_SCORE, 'power': 0})
    # 代理 ip 的不可用域名列表
    disable_domain = Column(MutableList.as_mutable(JSON), default=[])
    # 代理 ip 的来源
    origin = Column(String(128), default='')


# 创建所有继承 Base 类的所有的表
def init_db():
    Base.metadata.create_all(engine)


# 删除所有继承 Base 类的表
def drop_db():
    Base.metadata.drop_all(engine)


if __name__ == '__main__':
    # drop_db()
    init_db()

    session = Session()
    acc = session.query(Admin).count()
    import hashlib

    if acc == 0:
        admin = Admin(username='minco', password=hashlib.md5(('123' + settings.SECRET_KEY).encode()).hexdigest())
        session.add(admin)
        session.commit()
        session.close()
