from datetime import datetime
from flask import redirect, render_template, url_for, flash
from flask_login import current_user as cuser, login_required
from app import db
from app.main.order_states import bp
from app.models import OrderState
from app.main.forms import FindForm, AddForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if not cuser.is_admin: return redirect(url_for('index'))
    f = FindForm()
    add_form = AddForm(item='state')
    query = OrderState.query
    if f.submit.data and f.validate():
        search = f.s.data
        if search:
            query = query.filter(OrderState.order_state_label.like(f'%{search}%'))
    elif add_form.validate_on_submit():
        state = OrderState(order_state_label=add_form.label.data)
        try:
            db.session.add(state)
            db.session.commit()
            flash('состояние заказа!')
        except Exception as e:
            flash(f'Adding error: {e}')
        add_form.label.data = None
    return render_template("order_states/index.html",
                           title='состояния',
                           table_name='Состояния заказа',
                           data=query.all(),
                           query_form=f,
                           add_form=add_form)


@bp.route('/del/<int:id>')
@login_required
def delete(id):
    if cuser.isnt_admin:  return redirect(url_for('index'))
    state = OrderState.query.get_or_404(id)
    try:
        db.session.delete(state)
        db.session.commit()
    except Exception as e:
        flash(f'Нельзя')
    return redirect(url_for('.index'))