from flask import Blueprint

api_v1_app = Blueprint('api_v1', __name__, static_folder='../static')

from . import admin
