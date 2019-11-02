import json

from flask import request

from utils import logger
from models import Proxy
from utils.tools import object_to_dict
from utils.api_service import ApiService


@ApiService
def get_my_messages(ser):
    """
    获取当前用户所有的留言
    :param ser:
    :return:
    """

    session = ser.session
    proxies = session.query(Proxy).limit(10)

    res = {
        'proxies': [object_to_dict(proxy) for proxy in proxies]
    }

    return json.dumps(res)
