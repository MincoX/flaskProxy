import json
import hashlib
from datetime import datetime

from flask_wtf.csrf import generate_csrf
from sqlalchemy.orm.exc import NoResultFound
from flask import request, render_template, redirect, abort, jsonify, make_response
from flask_login import login_user, login_required, logout_user, current_user

import settings
from App import login_manager
from models import Session, Admin, AdminLoginLog
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
        remember = request.form.get('remember')
        # TODO
        #  remember account,
        account = session.query(Admin).filter(Admin.username == username).first()
        session.close()
        if account:
            if account.password == hashlib.md5((password + settings.SECRET_KEY).encode()).hexdigest():
                login_user(account, remember=True)
                login_log = AdminLoginLog(
                    admin_id=account.id,
                    ip=request.environ.get('HTTP_FORWARDED_FOR', request.remote_addr),
                    create_time=datetime.today(),
                )
                session.add(login_log)
                session.commit()
                session.close()
                return redirect('index')
            else:
                abort(403)
        else:
            return render_template('login.html', tip='account is not exist')


@api_v1_app.route('/login_out')
def login_out():
    logout_user()
    return redirect('/login/')


@api_v1_app.route('/index')
# @login_required
def index():
    return api_v1_app.send_static_file('index.html')


@api_v1_app.route('/api/<slug>/', methods=['POST', 'GET'])
# @login_required
def service(slug):
    session = Session()
    account = session.query(Admin).filter(Admin.id == 1).first()
    login_user(account, remember=True)
    res = service_view(slug)

    response = make_response(res)

    return res
