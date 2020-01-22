import json

from flask import request
from flask_login import current_user

import settings
from utils import logger
from models import Admin, Proxy
from utils.tools import object_to_dict, hour_range
from utils.api_service import ApiService, permission_api_service


# # @ApiService
@permission_api_service(perms=['base'])
def get_user_info(ser):
    """
    获取用户信息
    :param ser:
    :return:
    """
    session = ser.session
    user = session.query(Admin).get(current_user.id)

    res = {
        'status': 1,
        'user_info': [object_to_dict(user)],
        'identity': sorted([(role.slug, role.name) for role in user.roles], key=lambda x: x[0], reverse=True)[0][1]
    }

    del res['user_info'][0]['password']

    return json.dumps(res)


@permission_api_service(perms=['base'])
def post_update_user_info(server):
    """
    修改用户信息
    :param server:
    :return:
    """
    session = server.session
    user = session.query(Admin).get(current_user.id)

    img = request.form.get('imgBase64')
    username = request.form.get('username')
    password = request.form.get('password')
    phone = request.form.get('phone')
    birthday = request.form.get('birthday')
    address = request.form.get('address')
    email = request.form.get('email')
    personality = request.form.get('personality')

    user.username = username
    user.password = password
    user.birthday = birthday
    user.address = address
    user.phone = phone
    user.email = email
    user.personality = personality
    user.header = img

    session.commit()

    res = {
        'status': 1,
        'message': '信息修改成功'
    }

    return json.dumps(res)


if __name__ == '__main__':
    pass
