from flask import Blueprint

bp = Blueprint('dish_ctg', __name__)

from app.main.dish_ctg import routes