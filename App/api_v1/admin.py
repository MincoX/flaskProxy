import hashlib
import json

from flask_wtf.csrf import generate_csrf
from sqlalchemy.orm.exc import NoResultFound
from flask import request, render_template, redirect, abort, jsonify, make_response
from flask_login import login_user, login_required, logout_user, current_user

import settings
from App import login_manager
from models import Session, Admin
from App.api_v1 import api_v1_app
from utils.api_service import service_view


@login_manager.user_loader
def load_user(admin_id):
    session = Session()
    try:
        return session.query(Admin).filter(Admin.id == admin_id).one()
    except NoResultFound:
        return None
    finally:
        session.close()


@login_manager.unauthorized_handler
def unauthorized_callback():
    current_path = request.path
    return redirect('/login')


@api_v1_app.route('/register')
def register():
    session = Session()
    username = request.values.get('username')
    password = request.values.get('password')
    # TODO
    #  send email verify register
    account = Admin(username=username, password=hashlib.md5((password + settings.SECRET_KEY).encode()).hexdigest())
    session.add(account)
    session.commit()
    session.close()

    return redirect('/')


@api_v1_app.route('/')
@api_v1_app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        session = Session()
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')
        # TODO
        #  remember account,
        account = session.query(Admin).filter(Admin.username == username).first()
        session.close()
        if account:
            if account.password == hashlib.md5((password + settings.SECRET_KEY).encode()).hexdigest():
                login_user(account, remember=True)
                return redirect('index')
            else:
                abort(403)
        else:
            return render_template('login.html', tip='account is not exist')


@api_v1_app.route('/index')
@login_required
def index():
    return api_v1_app.send_static_file('index.html')


# @api_v1_app.after_request
# def after_request(response):
#     # 调用函数生成csrf token
#     csrf_token = generate_csrf()
#     # 设置cookie传给前端
#     response.set_cookie('csrf_token', csrf_token)
#     print(csrf_token + '*' * 100)
#     return response


@api_v1_app.route('/api/<slug>/', methods=['POST', 'GET'])
# @login_required
def service(slug):
    session = Session()
    account = session.query(Admin).first()
    login_user(account, remember=True)
    resp = make_response(str(service_view(slug)))
    resp.set_cookie('csrf_token', 'abctest')
    return resp
