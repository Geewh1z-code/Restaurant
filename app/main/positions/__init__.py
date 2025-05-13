from flask import Blueprint

bp = Blueprint('positions', __name__)

from app.main.positions import routes