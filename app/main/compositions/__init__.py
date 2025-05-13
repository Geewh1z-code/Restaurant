from flask import Blueprint

bp = Blueprint('compositions', __name__)

from app.main.compositions import routes