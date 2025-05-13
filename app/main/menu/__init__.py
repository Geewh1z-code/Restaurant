from flask import Blueprint

bp = Blueprint('menu', __name__)

from app.main.menu import routes
