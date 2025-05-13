from flask import redirect, render_template, url_for, flash
from flask_login import current_user as cuser, login_required
from app import db
from app.main.units import bp
from app.models import Unit
from app.main.forms import FindForm, AddForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if not cuser.is_admin:  return redirect(url_for('index'))
    f = FindForm()
    add_form = AddForm(item='unit')
    query = Unit.query
    if f.submit.data and f.validate():
        search = f.s.data
        if search:
            query = query.filter(Unit.unit_label.like(f'%{search}%'))
    elif add_form.validate_on_submit():
        unit = Unit(unit_label=add_form.label.data)
        try:
            db.session.add(unit)
            db.session.commit()
            flash('Unit added to base!')
        except Exception as e:
            flash(f'Adding error: {e}')
        add_form.label.data = None
    return render_template("units/index.html",
                           title='ЕИ',
                           table_name='Единицы измерения ингредиентов',
                           data=query.all(),
                           query_form=f,
                           add_form=add_form)


@bp.route('/del/<int:id>')
@login_required
def delete(id):
    if cuser.isnt_admin:  return redirect(url_for('index'))
    unit = Unit.query.get_or_404(id)
    try:
        db.session.delete(unit)
        db.session.commit()
    except Exception as e:
        flash(f'Нельзя')
    return redirect(url_for('.index'))