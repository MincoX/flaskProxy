from flask import Blueprint

api = Blueprint('api_mini_program', __name__, static_folder='../static')

from . import users
