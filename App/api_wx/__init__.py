from flask import Blueprint

api = Blueprint('api_wx', __name__, static_folder='../static')

from . import miniprogram
