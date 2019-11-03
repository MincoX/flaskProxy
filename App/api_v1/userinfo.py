import json

from flask_login import current_user

import settings
from utils import logger
from models import Admin, Proxy
from utils.tools import object_to_dict, hour_range
from utils.api_service import ApiService


@ApiService
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
        # 'identity': user.roles[:-1][0].name
    }

    logger.info(res)

    del res['user_info'][0]['password']
    del res['user_info'][0]['auth_key']

    return json.dumps(res)


if __name__ == '__main__':
    pass
