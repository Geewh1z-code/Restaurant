from flask import render_template
from flask_login import login_required
from app import db
from app.main.store import bp
from app.models import Ingredient, Store, Unit
from app.main.forms import FindTimeForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    f = FindTimeForm()
    query = db.session.query(Store.store_id, Store.ingr_id, Store.store_val, Store.counted_at,
                             Ingredient.ingr_label, Ingredient.unit_id, Unit.unit_label) \
        .join(Store).join(Unit)
    if f.validate_on_submit():
        search = f.s.data
        start = f.start.data
        end = f.until.data
        if search:
            query = query.filter(db.or_(Ingredient.ingr_label.like(f'%{search}%')
                                        ))
        if start:
            query = query.filter(Store.counted_at >= start)
        if end:
            query = query.filter(Store.counted_at <= end)
    return render_template("store/index.html",
                           title='Склад',
                           table_name='Склад ресторана',
                           data=query.all(),
                           query_form=f)