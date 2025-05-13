from flask import Blueprint

bp = Blueprint('places', __name__)

from app.main.places import routes
