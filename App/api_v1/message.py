import os
import json
from datetime import datetime

from flask import request
from flask_login import current_user
from werkzeug.utils import secure_filename

import settings
from utils import logger
from models import Proxy, Admin, Message
from utils.tools import object_to_dict
from utils.api_service import ApiService, permission_api_service


# @ApiService
@permission_api_service(perms=['base'])
def post_publish(ser):
    """
    发布留言
    :param ser:
    :return:
    """
    session = ser.session
    account = session.query(Admin).get(current_user.id)
    title = request.form.get('title')
    content = request.form.get('content')

    message = Message(
        title=title,
        content=content,
        admin_id=account.id,
        create_time=datetime.now()
    )

    session.add(message)
    session.commit()

    res = {
        'status': 1,
        'message_id': message.id,
        'message': '留言发布成功'
    }

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base'])
def get_announcement_message(ser):
    """
    获取公告信息
    :param ser:
    :return:
    """

    session = ser.session
    announcement = session.query(Message).filter(Message.admin_id == 1).order_by(Message.create_time.desc()).first()

    res = {
        'status': 1,
        'message': object_to_dict(announcement),
        'username': announcement.admin.username,
        'header': announcement.admin.header
    }

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base'])
def get_all_message(ser):
    """
    获取所有的留言
    :param ser:
    :return:
    """
    session = ser.session

    all_message_list = session.query(Message).order_by(Message.create_time.desc()).all()

    res = {
        'status': 1,
        'all_message_list': [
            {
                'username': per_message.admin.username,
                'header': per_message.admin.header,
                'message_id': per_message.id,
                'title': per_message.title,
                'content': per_message.content,
                'pub_time': per_message.create_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            for per_message in all_message_list
        ]
    }

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base'])
def post_message_detail(ser):
    """
    获取留言详情
    :param ser:
    :return:
    """

    session = ser.session
    message_id = request.form.get('message_id')

    message = session.query(Message).filter(Message.id == message_id).first()
    res = {
        'status': 1,
        'message': object_to_dict(message),
        'user_info': object_to_dict(message.admin)
    }
    del res['user_info']['password']
    del res['user_info']['auth_key']

    logger.info(res)

    return json.dumps(res)


# @ApiService
@permission_api_service(perms=['base'])
def get_my_message(ser):
    """
    获取用户的留言列表
    :param ser:
    :return:
    """
    session = ser.session
    user = session.query(Admin).get(current_user.id)

    messages = user.messages

    res = {
        'status': 1,
        'message_list': [
            {
                'message_id': per_message.id,
                'title': per_message.title,
                'content': per_message.content,
                'pub_time': per_message.create_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            for per_message in messages
        ]
    }

    return json.dumps(res)


@permission_api_service(perms=['base'])
def post_upload_img(ser):
    """
    上传图片
    :return:
    """
    file = request.files.get('file')
    filename = secure_filename(file.filename)
    file.save(os.path.join(settings.UPLOAD_FOLDER, filename))

    res = {
        'status': 1,
        'uploaded': 1,
        'fileName': f'{filename}',
        'url': f'App/static/upload/{filename}',
    }

    return json.dumps(res)
