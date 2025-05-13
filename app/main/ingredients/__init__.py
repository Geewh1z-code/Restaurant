from flask import Blueprint

bp = Blueprint('ingredients', __name__)

from app.main.ingredients import routes