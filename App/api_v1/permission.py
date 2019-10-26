import json
from datetime import datetime

from flask import request

from utils import logger
from models import Perm, Role, Admin
from utils.tools import object_to_dict
from utils.api_service import ApiService


@ApiService
def get_perms(ser):
    """
    获取数据库中的所有权限
    :return:
    """
    session = ser.session
    perms = session.query(Perm).all()
    perms = [object_to_dict(perm) for perm in perms]

    return json.dumps(perms)


@ApiService
def get_roles(ser):
    """
    获取数据库中的所有角色
    :return:
    """
    session = ser.session
    roles = session.query(Role).all()

    res = [
        {
            'id': role.id,
            'name': role.name,
            'slug': role.slug,
            'perms': [object_to_dict(perm) for perm in role.perms]
        }
        for role in roles
    ]

    return json.dumps(res)


@ApiService
def get_admins(ser):
    """
    获取管理员分配的角色情况
    :return:
    """
    session = ser.session
    admins = session.query(Admin).all()

    res = [
        {
            'id': admin.id,
            'username': admin.username,
            'create_time': admin.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'roles': [object_to_dict(role) for role in admin.roles],
        }
        for admin in admins
    ]

    logger.info(res)

    return json.dumps(res)


@ApiService
def post_add_perm(ser):
    """
    添加权限
    :param ser:
    :return:
    """
    session = ser.session
    name = request.form.get('name')
    slug = request.form.get('slug')

    perm = Perm(name=name, slug=slug)
    session.add(perm)
    session.commit()

    res = {
        'status': 'success',
        'message': '权限添加成功'
    }

    return json.dumps(res)
