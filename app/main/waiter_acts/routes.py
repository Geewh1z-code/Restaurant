from datetime import datetime
from flask import redirect, render_template, url_for, flash
from flask_login import current_user as cuser, login_required
from app import db
from app.main.waiter_acts import bp
from app.models import User, Role, Place, WaiterAct
from app.main.forms import FindTimeForm, WaiterActForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if not cuser.has_role('waiter'): return redirect(url_for('index'))
    f = FindTimeForm()

    waiters = User.query.join(User.roles).filter(Role.role_label == 'waiter')
    # Список занятых столов на данный день с отношением 6 гостей на 1 официанта
    z_places = db.session.query(WaiterAct.place_id) \
        .join(Place).filter(WaiterAct.works_at == datetime.today().date()).group_by(WaiterAct.place_id,
                                                                                    Place.place_capacity) \
        .having((Place.place_capacity / db.func.count(WaiterAct.user_id)) <= 6)
    # Список недораспределенных столов
    places = Place.query.filter(Place.place_id.not_in(z_places)).order_by(Place.place_label)

    add_form = WaiterActForm()
    add_form.waiter.choices = [w.to_touple() for w in waiters]
    add_form.place.choices = [p.to_touple() for p in places]

    query = db.session.query(WaiterAct.waiter_act_id, WaiterAct.works_at,
                             WaiterAct.user_id, User.user_fullname,
                             WaiterAct.place_id, Place.place_label,
                             Place.place_capacity).join(User).join(Place)

    if f.submit.data and f.validate():
        search = f.s.data
        start = f.start.data
        end = f.until.data
        if search:
            query = query.filter(db.or_(Place.place_label.like(f'%{search}%'),
                                        Place.place_capacity.like(f'{search}'),
                                        User.user_fullname.like(f'%{search}%')))
        if start:
            query = query.filter(WaiterAct.works_at >= start)
        if end:
            query = query.filter(WaiterAct.works_at <= end)

    elif add_form.validate_on_submit():
        wact = WaiterAct(user_id=add_form.waiter.data, place_id=add_form.place.data)
        try:
            db.session.add(wact)
            db.session.commit()
            flash('Дежурство добавлено!')
        except Exception as e:
            flash(f'Adding error: {e}')
        return redirect(url_for('.index'))
    return render_template("waiter_acts/index.html",
                           title='Официанты',
                           table_name='Акты о сменах официантов',
                           data=query.all(),
                           query_form=f,
                           add_form=add_form)


@bp.route('/del/<int:id>')
@login_required
def delete(id):
    if cuser.isnt_admin:  return redirect(url_for('index'))
    wact = WaiterAct.query.get_or_404(id)
    try:
        db.session.delete(wact)
        db.session.commit()
    except Exception as e:
        flash(f'нельзя')
    return redirect(url_for('.index'))
