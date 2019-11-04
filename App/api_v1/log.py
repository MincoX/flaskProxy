import json
from datetime import datetime, timedelta

from flask import request
from flask_login import current_user
from sqlalchemy import cast, DATE, func, and_

import settings
from utils import logger
from models import Admin, Proxy, AdminLoginLog
from utils.tools import object_to_dict, hour_range
from utils.api_service import ApiService, permission_api_service


# @ApiService
@permission_api_service(perms=['base'])
def get_login_log(ser):
    """
    获取登录日志
    :param ser:
    :return:
    """
    session = ser.session
    login_logs = session.query(AdminLoginLog).order_by(AdminLoginLog.create_time.desc()).all()
    res = {
        'status': 1,
        'login_info': [
            {
                'id': login_log.admin.id,
                'ip': login_log.ip,
                'username': login_log.admin.username,
                'log_create_time': login_log.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'account_create_time': login_log.admin.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'active': login_log.admin.active
            }
            for login_log in login_logs
        ]
    }

    return json.dumps(res)
