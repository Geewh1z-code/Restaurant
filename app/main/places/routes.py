from flask import redirect, render_template, url_for, flash
from flask_login import current_user as cuser, login_required
from app import db
from app.main.places import bp
from app.models import Place
from app.main.forms import FindForm, PlaceForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if not cuser.is_admin:  return redirect(url_for('index'))
    f = FindForm()
    add_form = PlaceForm()
    query = Place.query
    if f.submit.data and f.validate():
        search = f.s.data
        if search:
            query = query.filter(Place.place_capacity.like(f'%{search}%'))
    elif add_form.validate_on_submit():
        place = Place(place_label=add_form.label.data, place_capacity=add_form.capacity.data)
        try:
            db.session.add(place)
            db.session.commit()
            flash('Столик сохранен!')
        except Exception as e:
            flash(f'Adding error: {e}')
        return redirect(url_for('.index'))
    return render_template("places/index.html",
                           title='Столы',
                           data=query.order_by(Place.place_label).all(),
                           query_form=f,
                           table_name='Столы и залы',
                           add_form=add_form)


@bp.route('/del/<int:id>')
@login_required
def delete(id):
    if cuser.isnt_admin:  return redirect(url_for('index'))
    place = Place.query.get_or_404(id)
    try:
        db.session.delete(place)
        db.session.commit()
    except Exception as e:
        flash(f'Нельзя')
    return redirect(url_for('.index'))