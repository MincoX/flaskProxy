from datetime import datetime

from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, Table, \
    ForeignKey, DateTime, func, Boolean, Text, LargeBinary

import settings

engine = create_engine(
    "mysql+mysqlconnector://root:root@49.232.19.51:33061/proxy_server",
    max_overflow=0,  # 超过连接池大小外最多创建的连接
    pool_size=200,  # 连接池大小
    pool_timeout=10,  # 连接池中没有已建立的连接时，新建立 http 连接最多等待的时间
    pool_recycle=30,  # session 对象被重置，防止 mysql 清除建立的 http 连接后，session 对象还保持原有会话而报错
)

Base = declarative_base()
Session = sessionmaker(bind=engine)

rel_admin_role = Table(
    'rel_admin_role', Base.metadata,
    Column('admin_id', Integer, ForeignKey('admin.id')),
    Column('role_id', Integer, ForeignKey('role.id'))
)

rel_role_perm = Table(
    'rel_role_perm', Base.metadata,
    Column('role_id', Integer, ForeignKey('role.id')),
    Column('perm_id', Integer, ForeignKey('perm.id'))
)

protocol_map = {
    -1: '不可用',
    0: 'http',
    1: 'https',
    2: 'http/https'
}

nick_type_map = {
    -1: '不可用',
    0: '高匿',
    1: '匿名',
    2: '透明'
}


class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True, nullable=False)
    slug = Column(String(32), unique=True, nullable=False)

    admins = relationship('Admin', secondary=rel_admin_role, back_populates='roles')
    perms = relationship('Perm', secondary=rel_role_perm, back_populates='roles')


class Perm(Base):
    __tablename__ = 'perm'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True, nullable=False)
    slug = Column(String(32), unique=True, nullable=False)

    roles = relationship('Role', secondary=rel_role_perm, back_populates='perms')


class Admin(Base):
    __tablename__ = 'admin'

    id = Column(Integer, primary_key=True)
    username = Column(String(128), unique=True, nullable=False)
    password = Column(String(256), nullable=False)
    active = Column(Boolean, default=True)
    header = Column(LargeBinary, nullable=True)
    auth_key = Column(String(256), default='')
    birthday = Column(DateTime(timezone=True), nullable=True)
    address = Column(String(128), nullable=True, default='')
    personality = Column(String(256), nullable=True, default='')
    create_time = Column(DateTime(timezone=True), default=func.now())

    roles = relationship('Role', secondary=rel_admin_role, back_populates='admins')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def get_perms(self):
        perms = []
        for role in self.roles:
            for perm in role.perms:
                perms.append((perm.slug, perm.name))
        return list(set(perms))

    def __repr__(self):
        return f'{self.id}:{self.username}'


class AdminLoginLog(Base):
    __tablename__ = 'admin_login_log'

    id = Column(Integer, primary_key=True)
    ip = Column(String(32), default='127.0.0.1')
    create_time = Column(DateTime(timezone=True), default=func.now())

    admin_id = Column(Integer, ForeignKey('admin.id'))
    # lazy=select, return all object,  lazy=dynamic, return query object
    admin = relationship('Admin', backref=backref('logs', lazy='select'))


class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    title = Column(String(128), default='')
    content = Column(Text)
    status = Column(Integer, default=0)
    create_time = Column(DateTime(timezone=True), default=func.now())

    admin_id = Column(Integer, ForeignKey('admin.id'))
    admin = relationship('Admin', backref=backref('messages', lazy='select'))


class Proxy(Base):
    __tablename__ = 'proxy'

    id = Column(Integer, primary_key=True)
    ip = Column(String(64))
    port = Column(String(64))
    # http:0, https:1, http/https:2
    protocol = Column(Integer, default=-1)
    # 高匿：0， 匿名：1， 透明：2
    nick_type = Column(Integer, default=-1)
    # speed : -1, ip 不可用
    speed = Column(Float, default=-1)
    area = Column(String(255), default='')
    score = Column(MutableDict.as_mutable(JSON), default={'score': settings.MAX_SCORE, 'power': 0})
    # 代理 ip 的不可用域名列表
    disable_domain = Column(MutableList.as_mutable(JSON), default=[])
    origin = Column(String(128), default='')
    create_time = Column(DateTime(timezone=True), default=func.now())


class CeleryTask(Base):
    __tablename__ = 'celery_task'

    id = Column(Integer, primary_key=True)
    task_id = Column(String(128), default='')
    task_name = Column(String(128), default='')
    task_status = Column(Integer, default=1)
    start_time = Column(DateTime(timezone=True), default=func.now())
    end_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    consume = Column(String(128), default='')
    harvest = Column(Integer, nullable=True)


def init_db():
    Base.metadata.create_all(engine)


def drop_db():
    Base.metadata.drop_all(engine)


if __name__ == '__main__':
    # drop_db()
    init_db()

    from perm_init import init_system

    init_system()
