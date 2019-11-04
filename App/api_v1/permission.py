import json
import hashlib

from flask import request

import settings
from utils import logger
from models import Perm, Role, Admin
from utils.tools import object_to_dict
from utils.api_service import ApiService, permission_api_service


# @ApiService
@permission_api_service(perms=['base'])
def get_perms(ser):
    """
    获取数据库中的所有权限
    :return:
    """
    session = ser.session
    perms = session.query(Perm).all()
    perms = [object_to_dict(perm) for perm in perms]

    return json.dumps(perms)


# @ApiService
@permission_api_service(perms=['base'])
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


# @ApiService
@permission_api_service(perms=['base'])
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
            'active': admin.active,
            'roles': [object_to_dict(role) for role in admin.roles],
        }
        for admin in admins
    ]

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base'])
def post_add_perm(ser):
    """
    添加权限
    :param ser:
    :return:
    """
    session = ser.session

    name = request.form.get('name')
    slug = request.form.get('slug')

    if session.query(Perm).filter(Perm.name == name).first():
        res = {
            'status': 0,
            'message': '权限已经存在'
        }
        return json.dumps(res)

    perm = Perm(name=name, slug=slug)
    session.add(perm)
    session.commit()

    res = {
        'status': 1,
        'message': '权限添加成功'
    }

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base', 'do_setting', 'do_auth'])
def post_del_perm(ser):
    """
    删除权限
    :param ser:
    :return:
    """
    session = ser.session

    perm = session.query(Perm).get(request.form.get('perm_id'))
    session.delete(perm)
    session.commit()

    res = {
        'status': 1,
        'message': '权限删除成功'
    }

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base'])
def post_role_perms(ser):
    """
    获取角色对应的权限
    :param ser:
    :return:
    """
    session = ser.session
    slug = request.form.get('slug')
    perms = session.query(Role).filter(Role.slug == slug).first().perms
    res = {
        'status': 1,
        'perms': [object_to_dict(perm) for perm in perms],
    }

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base', 'do_setting', 'do_auth'])
def post_set_perm(ser):
    """
    修改角色分配的权限
    :param ser:
    :return:
    """
    session = ser.session

    role = session.query(Role).get(request.form.get('role_id'))
    new_perms = json.loads(request.form.get('new_perms'))
    role_perms = [object_to_dict(perm)['slug'] for perm in role.perms]

    add_perms = [p['slug'] for p in new_perms if p.get('selected') is True and p['slug'] not in role_perms]
    remove_perms = [p['slug'] for p in new_perms if p.get('selected') is False and p['slug'] in role_perms]

    add_perms = session.query(Perm).filter(Perm.slug.in_(add_perms)).all()
    for per in add_perms:
        role.perms.append(per)

    remove_perms = session.query(Perm).filter(Perm.slug.in_(remove_perms)).all()
    for per in remove_perms:
        role.perms.remove(per)

    session.commit()

    res = {
        'status': 1,
        'message': '权限配置成功'
    }

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base'])
def post_user_roles(ser):
    """
    获取用户所拥有的角色
    :param ser:
    :return:
    """
    session = ser.session

    user = session.query(Admin).get(request.form.get('user_id'))
    user_roles = [object_to_dict(role) for role in user.roles]

    res = {
        'status': 1,
        'roles': user_roles,
    }

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base', 'do_setting', 'do_auth'])
def post_set_role(ser):
    """
    为用户设置角色
    :param ser:
    :return:
    """
    session = ser.session
    user = session.query(Admin).get(request.form.get('user_id'))
    new_roles = json.loads(request.form.get('new_roles'))
    user_roles = [object_to_dict(role)['slug'] for role in user.roles]

    add_roles = [p['slug'] for p in new_roles if p.get('selected') is True and p['slug'] not in user_roles]
    remove_perms = [p['slug'] for p in new_roles if p.get('selected') is False and p['slug'] in user_roles]

    add_roles = session.query(Role).filter(Role.slug.in_(add_roles)).all()
    for per in add_roles:
        user.roles.append(per)

    remove_roles = session.query(Role).filter(Role.slug.in_(remove_perms)).all()
    for per in remove_roles:
        user.roles.remove(per)

    session.commit()

    res = {
        'status': 1,
        'message': '角色配置成功'
    }

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base'])
def post_add_role(ser):
    """
    添加角色
    :param ser:
    :return:
    """
    session = ser.session

    slug = request.form.get('slug')
    name = request.form.get('name')
    if session.query(Role).filter(Role.name == name).first():
        res = {
            'status': 0,
            'message': '角色已经存在'
        }
        return json.dumps(res)

    role = Role(slug=slug, name=name)
    session.add(role)
    session.commit()

    res = {
        'status': 1,
        'message': '角色添加成功'
    }

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base', 'do_setting', 'do_auth'])
def post_del_role(ser):
    """
    删除角色
    :param ser:
    :return:
    """
    session = ser.session

    role = session.query(Role).get(request.form.get('role_id'))
    session.delete(role)
    session.commit()

    res = {
        'status': 1,
        'message': '角色删除成功'
    }

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base', 'do_setting', 'do_auth'])
def post_add_admin(ser):
    """
    添加管理员
    :param ser:
    :return:
    """
    session = ser.session

    username = request.form.get('username')
    password = request.form.get('password')
    password = hashlib.md5((password + settings.SECRET_KEY).encode()).hexdigest()

    if session.query(Admin).filter(Admin.username == username).first():
        res = {
            'status': 0,
            'message': '管理员已经存在'
        }
        return json.dumps(res)

    admin = Admin(username=username, password=password)
    session.add(admin)
    session.commit()

    res = {
        'status': 1,
        'message': '管理员添加成功'
    }

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base', 'do_setting', 'do_auth'])
def post_toggle_active(ser):
    """
    账户激活状态切换
    :param ser:
    :return:
    """
    session = ser.session

    uid = request.form.get('uid')
    cur_active = request.form.get('active')
    new_active = True if cur_active == 'false' else False

    admin = session.query(Admin).get(uid)
    admin.active = new_active
    session.commit()

    res = {
        'status': 1,
        'message': '账户状态切换成功'
    }

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base', 'do_setting', 'do_auth', 'test'])
def post_reset_password(ser):
    """
    重置密码
    :param ser:
    :return:
    """
    session = ser.session
    admin = session.query(Admin).get(request.form.get('uid'))

    init_pwd = hashlib.md5(('123456' + settings.SECRET_KEY).encode()).hexdigest()
    admin.password = init_pwd
    session.commit()

    res = {
        'status': 1,
        'message': '重置密码成功'
    }

    return json.dumps(res)
