from flask import Blueprint

bp = Blueprint('waybills', __name__)

from app.main.waybills import routes