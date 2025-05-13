from flask import Blueprint

bp = Blueprint('store', __name__)

from app.main.store import routes