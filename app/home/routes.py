from flask import render_template
from app import app


@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def index():
    return render_template('home/index.html', title='Дом')
