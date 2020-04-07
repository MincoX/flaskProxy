import requests


def handle_request(url, data=None, method="GET"):
    """
    微信统一请求接口
    :param url:
    :param data:
    :param method:
    :return:
    """
    if method == "GET":
        res = requests.get(url, params=data)
        if res.code is 0:
            return handle_success(res)
        else:
            return handle_error(res)

    if method == "POST":
        res = requests.post(url, data=data)
        print("handle_success >>> ", res)
        if res.code is 0:
            return handle_success(res)
        else:
            return handle_error(res)


def handle_response(res):
    if res.statusCode is 200:
        return handle_success(res)
    else:
        return handle_error(res)


def handle_success(res):
    res = {
        "code": 200,
        "data": res.data,
        "msg": res.errmsg
    }

    return res


def handle_error(res):
    res = {
        "code": 0,
        "data": res.data,
        "msg": res.errmsg
    }

    return res
