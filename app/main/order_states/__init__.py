from flask import Blueprint

bp = Blueprint('order_states', __name__)

from app.main.order_states import routes