from flask import redirect, render_template, url_for, flash
from flask_login import current_user as cuser, login_required
from datetime import datetime
from app import db
from app.main.orders import bp
from app.models import Menu, Order, OrderState, WaiterAct, User, Place, Position as Pos, Dish
from app.main.forms import EditOrderForm, FindTimeForm, OrderForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    f = FindTimeForm()
    add_form = OrderForm()
    places = Place.query.join(WaiterAct).filter(db.and_(WaiterAct.user_id == cuser.id,
                                                        WaiterAct.works_at == datetime.today().date()))
    add_form.waiter.choices = [cuser.to_touple()]
    add_form.place.choices = [place.to_touple() for place in places.all()]
    # Сумма на каждый счет
    y = db.session.query(Order.order_id, (db.func.sum(Pos.position_val * Menu.menu_price)).label('pos_sum')) \
        .group_by(Order.order_id) \
        .join(Order, Order.order_id == Pos.order_id) \
        .join(Dish).join(Menu).filter(Menu.created_at == Order.ordered_at).subquery()
    query = db.session.query(Order.order_id, Order.order_state_id, OrderState.order_state_label,
                             Order.order_total, Order.order_code, Order.ordered_at,
                             Order.place_id, Place.place_label, Place.place_capacity,
                             WaiterAct.user_id, User.user_fullname, y.c.pos_sum) \
        .join(OrderState).join(Place) \
        .join(WaiterAct, WaiterAct.place_id == Order.place_id) \
        .filter(WaiterAct.works_at == Order.ordered_at) \
        .join(User, User.id == WaiterAct.user_id).outerjoin(y, y.c.order_id == Order.order_id)
    if f.submit.data and f.validate():
        search = f.s.data
        start = f.start.data
        end = f.until.data
        if search:
            query = query.filter(db.or_(Order.order_id.like(f'%{search}%'),
                                        Order.order_code.like(f'%{search}%'),
                                        User.user_fullname.like(f'%{search}%'),
                                        Order.order_total >= search))
        if start:
            query = query.filter(Order.ordered_at >= start)
        if end:
            query = query.filter(Order.ordered_at <= end)
        print(query)
    elif add_form.validate_on_submit():
        order = Order(order_code=add_form.code.data, place_id=add_form.place.data)
        try:
            db.session.add(order)
            db.session.commit()
            flash('Заказ добавлен!')
        except Exception as e:
            flash(f'Adding error: {e}')
        return redirect(url_for('.index'))

    return render_template("orders/index.html",
                           title='Заказы',
                           data=query.all(),
                           query_form=f,
                           table_name='Заказы',
                           add_form=add_form)


@bp.route('/del/<int:id>')
@login_required
def delete(id):
    if cuser.isnt_admin:  return redirect(url_for('index'))
    order = Order.query.get_or_404(id)
    try:
        db.session.delete(order)
        db.session.commit()
    except Exception as e:
        flash(f'Нельзя')
    return redirect(url_for('.index'))


@bp.route('/pay/<int:id>')
@login_required
def pay(id):
    order = Order.query.get_or_404(id)
    # переносим сумму из выражения в базу (избыточная колонка)
    y = db.session.query(Order.order_id, (db.func.sum(Pos.position_val * Menu.menu_price)).label('pos_sum')) \
        .group_by(Order.order_id) \
        .join(Order, Order.order_id == Pos.order_id) \
        .join(Dish).join(Menu).filter(Menu.created_at == Order.ordered_at).filter(Order.order_id == id).first()
    if y.pos_sum and y.pos_sum > 0:
        order.order_total = y.pos_sum
        order.order_state_id = OrderState.query.filter(OrderState.order_state_label == 'payed').first().order_state_id
        try:
            db.session.commit()
        except Exception as e:
            flash(f'error')
    flash(f'Заказ #{id} оплачен')
    return redirect(url_for('.index'))


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    order = Order.query.get_or_404(id)
    f = EditOrderForm(old=order.order_code, code=order.order_code)
    if f.validate_on_submit():
        order.order_code = f.code.data
        try:
            db.session.commit()
        except Exception as e:
            flash(f'ошибка: {e}')
        return redirect(url_for('.index'))
    else:
        return render_template('form.html',
                               title=f'Изменить заказ {order.order_id}',
                               form=f)