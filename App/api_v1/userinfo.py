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
        'user': [object_to_dict(user)]
    }

    logger.info(res)

    return json.dumps(res)


if __name__ == '__main__':
    print(get_user_info())
