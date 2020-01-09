import json
import hashlib
import datetime

from flask_wtf.csrf import generate_csrf
from sqlalchemy.orm.exc import NoResultFound
from flask_login import login_user, login_required, logout_user, current_user
from flask import request, render_template, redirect, abort, jsonify, make_response

import settings
from App import login_manager
from App.api_v1 import api_v1_app
from models import Session, Admin, AdminLoginLog
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


@api_v1_app.route('/register', methods=['GET', 'POST'])
def register():
    session = Session()
    username = request.form.get('username')
    password = request.form.get('password')
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

        account = session.query(Admin).filter(Admin.username == username).first()
        if account:
            if account.password == hashlib.md5((password + settings.SECRET_KEY).encode()).hexdigest():
                login_user(account)
                login_log = AdminLoginLog(
                    admin_id=account.id,
                    ip=request.environ.get('X-Forwarded-For', request.remote_addr),
                    create_time=datetime.datetime.now(),
                )
                session.add(login_log)
                session.commit()
                session.close()

                return redirect('index')

            else:
                return render_template('login.html', tip='用户名或密码错误')
        else:
            return render_template('login.html', tip='用户不存在，请先注册')


@api_v1_app.route('/login_out')
@login_required
def login_out():
    logout_user()
    res = {
        'status': 1
    }
    return json.dumps(res)


@api_v1_app.route('/index')
@login_required
def index():
    return api_v1_app.send_static_file('index.html')


@api_v1_app.route('/api/<slug>/', methods=['POST', 'GET'])
# @login_required
def service(slug):
    session = Session()
    account = session.query(Admin).filter(Admin.username == 'MincoX').first()
    login_user(account, remember=True)

    res = service_view(slug)
    response = make_response(res)

    return response


@api_v1_app.route('/socket_io', methods=['GET'])
def socket_io_api():
    """
    socket io page
    :return:
    """
    return render_template('socket_io.html')
