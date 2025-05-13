from datetime import datetime
from flask import redirect, render_template, url_for, flash
from flask_login import current_user as cuser, login_required
from app import db
from app.main.positions import bp
from app.models import OrderState, Position as Pos, Dish, Order, Menu, User, Store, Composition as Comp
from app.main.forms import EditPosForm, FindSelForm, AddPosForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    today = datetime.today().date()
    f = FindSelForm()
    choices = [(0, 'All dishes')]
    for d in Order.query.filter(Order.ordered_at == today).all(): choices.append(d.to_touple())
    f.sel.choices = choices

    add_form = AddPosForm()
    state_id = OrderState.query.filter(OrderState.order_state_label == 'ordering').first().order_state_id
    orders = Order.query.filter_by(order_state_id=state_id, ordered_at=today)
    dishes = Dish.query.join(Menu).filter(Menu.created_at == today)
    add_form.order.choices = [o.to_touple() for o in orders.all()]
    add_form.dish.choices = [d.to_touple() for d in dishes.all()]

    query = db.session.query(Pos.position_id, Pos.position_val,
                             Pos.user_id,
                             Pos.order_id, Order.order_state_id, OrderState.order_state_label,
                             Pos.dish_id, Dish.dish_label, Menu.menu_price) \
        .join(Order, Order.order_id == Pos.order_id).join(OrderState) \
        .join(Dish).join(Menu).filter(Menu.created_at == Order.ordered_at)
    if f.submit.data and f.validate():
        sel = f.sel.data
        search = f.s.data
        if sel and sel != '0':
            query = query.filter(Order.order_id == sel)
        if search:
            query = query.filter(db.or_(Dish.dish_label.like(f'%{search}%'),
                                        User.user_fullname.like(f'%{search}%'),
                                        Menu.menu_price.like(f'%{search}%')))
    elif add_form.validate_on_submit():
        p = Pos(dish_id=add_form.dish.data, position_val=add_form.val.data, order_id=add_form.order.data)
        try:
            db.session.add(p)
            db.session.commit()
            flash('Пункт заказа добавлен!')
        except Exception as e:
            flash(f'Adding error: {e}')
        return redirect(url_for('.index'))

    return render_template("positions/index.html",
                           title='Пункты заказа',
                           data=query.all(),
                           query_form=f,
                           table_name='Пункты заказа',
                           add_form=add_form)


@bp.route('/del/<int:id>')
@login_required
def delete(id):
    if cuser.isnt_admin:  return redirect(url_for('index'))
    pos = Pos.query.get_or_404(id)
    try:
        db.session.delete(pos)
        db.session.commit()
    except Exception as e:
        flash(f'Нельзя')
    return redirect(url_for('.index'))


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    pos = Pos.query.get_or_404(id)
    f = EditPosForm(val=pos.position_val)
    if f.validate_on_submit():
        pos.position_val = f.val.data
        try:
            db.session.commit()
        except Exception as e:
            flash(f' {e}')
        return redirect(url_for('.index'))
    else:
        return render_template('form.html',
                               title=f'Изменить количество: {pos.dish.dish_label}',
                               form=f)


@bp.route('/cook/<int:id>')
@login_required
def cook(id):
    if not cuser.has_role('cook'):  return redirect(url_for('index'))
    today = datetime.now().strftime('%Y-%m-%d')
    pos = Pos.query.get_or_404(id)
    pos.user_id = cuser.id
    dish_id = int(pos.dish_id)
    ingrs = Comp.query.filter(Comp.dish_id == dish_id)
    for ingr in ingrs:
        store = Store.query.filter(Store.ingr_id == ingr.ingr_id).order_by(Store.counted_at.desc()).first()
        tmp = store.store_val - pos.position_val * ingr.comp_val
        if store.counted_at.strftime('%Y-%m-%d') == today:
            store.store_val = tmp
        else:
            nstore = Store(ingr_id=ingr.ingr_id, store_val=tmp)
            db.session.add(nstore)

    try:
        db.session.commit()
    except Exception as e:
        flash(f'Error')
    return redirect(url_for('.index'))
