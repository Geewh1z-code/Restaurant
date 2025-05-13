from flask import Blueprint

bp = Blueprint('units', __name__)

from app.main.units import routes
