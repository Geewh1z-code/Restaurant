from flask import Blueprint

bp = Blueprint('dishes', __name__)

from app.main.dishes import routes