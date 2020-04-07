import requests
from flask import request

from App.api_wx import api
from .wx_config import MiniProgram
from utils import wx_http


@api.route('/mp/getSession')
def get_session():
    js_code = request.data
    url = f"https://api.weixin.qq.com/sns/jscode2session?" \
          f"appid={MiniProgram.AppId}&secret={MiniProgram.AppSec}&js_code={js_code}&grant_type=authorization_code"

    res = wx_http.handle_request(url)
    print("wx_http.handle_request(url)", res)
    res = requests.get(url)
    print('requests.get(url) >>> ', res)
    return 'hello world'
