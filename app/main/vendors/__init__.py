from flask import Blueprint

bp = Blueprint('vendors', __name__)

from app.main.vendors import routes