from flask import Blueprint

bp = Blueprint('orders', __name__)

from app.main.orders import routes
