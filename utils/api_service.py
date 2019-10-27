import json
import types
import logging
import traceback
import importlib

from flask import request, abort

from utils import logger
from models import Session, Proxy


class Service:

    def __init__(self, session):
        self.session = session


class ApiService:

    def __init__(self, func):
        # 程序开启，装饰器被加载到内存中，此时 api session 被创建，以后不再创建
        self.session = Session()
        print(f'api session >>> {id(self.session)}')
        self.func = func

    def func_decorate(self, *args, **kwargs):
        try:
            # 每一个视图函数，都会去创建一个 Service (即每个视图函数的 session 不同，但是同一个视图函数中的 session 是同一个对象)
            service = Service(self.session)
            print(f'view session >>> {id(service.session)}')
            return self.func(service, *args, **kwargs)

        except Exception as e:
            print(e)
            logging.error(traceback.format_exc(limit=None))

        finally:
            print(f'session close {self.session}')
            self.session.close()

    def __call__(self, *args, **kwargs):
        return self.func_decorate(*args, **kwargs)


def service_view(slug):
    module_name, func_name = slug.split('.')

    if request.method == 'GET':
        module = importlib.import_module(f'App.api_v1.{module_name}')
        service_obj = getattr(module, f'get_{func_name}')
        ret = service_obj(**request.args.to_dict())
    else:
        module = importlib.import_module(f'App.api_v1.{module_name}')
        service_obj = getattr(module, f'post_{func_name}')

        ret = service_obj(**request.args.to_dict())
        # ret = service_obj(json.loads(request.data.decode('utf-8')))

    # 判断 api 接口是不是 ApiService 的实例（即 api 接口是不是添加了 ApiService 装饰器（因为后期会在装饰器中进行权限校验））
    # if type(service_obj) in (types.MethodType, ApiService):
    #
    #     if type(service_obj) == types.MethodType and service_obj.__self__.__class__ != ApiService:
    #         return abort(403)
    #     return ret
    #
    # return abort(403)

    return ret


@ApiService
def test(service):
    session = service.session
    print(f'index session {id(session)}')
    res = session.query(Proxy).first()


if __name__ == '__main__':
    # module = importlib.import_module('App.api_v1.dashboard')
    # func = module.get_navigate
    # print(func)
    # print(module)
    test()
