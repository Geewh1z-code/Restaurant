from flask import Blueprint

bp = Blueprint('waiter_acts', __name__)

from app.main.waiter_acts import routes