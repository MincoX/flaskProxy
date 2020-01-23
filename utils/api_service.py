import json
import types
import logging
import traceback
import importlib

from flask import request, abort
from flask_login import current_user

from utils import logger
from models import Session, Proxy, Admin


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


def check_perms(session, perms):
    if not perms:
        perms = ['base']

    if current_user.__tablename__ != 'admin':
        abort(403)

    current_admin = session.query(Admin).filter(Admin.id == current_user.id).one()
    perm_slugs = set([slug for slug, name in current_admin.get_perms()])

    return perm_slugs >= set(perms)


def permission_api_service(perms=None):
    session = Session()

    def func_wrapper(func):

        def _wrapper(*args, **kwargs):
            if current_user.__tablename__ == 'admin':
                if not check_perms(session, perms):
                    # abort(403)
                    return json.dumps({
                        'status': 0,
                        'message': '你的身份受限，操作失败！'
                    })
            # if current_user.__tablename__ == 'account':
            #     # perms is not None and perms unequal to base
            #     if not (perms == ['base'] or perms is None):
            #         abort(403)
            try:
                serve = Service(session)
                return func(serve, *args, **kwargs)
            except Exception as e:
                logger.error(e)
                logging.error(traceback.format_exc())
                return json.dumps({
                    'status': 0,
                    'message': '网络拥塞，请求失败！'
                })
            finally:
                session.close()

        return _wrapper

    return func_wrapper


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
