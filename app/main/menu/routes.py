from datetime import datetime
from flask import redirect, render_template, url_for, flash
from flask_login import current_user as cuser, login_required
from app import db
from app.main.menu import bp
from app.models import DishCategory, Menu, Dish
from app.main.forms import EditPriceForm, MenuForm, FindTimeForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    f = FindTimeForm()
    z_dishes = db.session.query(Menu.dish_id).filter(Menu.created_at == datetime.today().date())
    dishes = Dish.query.filter(Dish.dish_id.not_in(z_dishes)).order_by(Dish.dish_label)

    add_form = MenuForm()
    add_form.dish.choices = [d.to_touple() for d in dishes]
    query = db.session.query(Menu.dish_id, Menu.menu_id, Menu.menu_price,
                             Dish.dish_label, Dish.dish_category_id,
                             DishCategory.dish_category_label,
                             Menu.created_at).join(Dish, Dish.dish_id == Menu.dish_id).join(DishCategory)
    if f.submit.data and f.validate():
        search = f.s.data
        start = f.start.data
        end = f.until.data
        if search:
            query = query.filter(db.or_(Dish.dish_label.like(f'%{search}%'),
                                        DishCategory.dish_category_label.like(f'%{search}%')))
        if start:
            query = query.filter(Menu.created_at >= start)
        if end:
            query = query.filter(Menu.created_at <= end)

    elif add_form.validate_on_submit():
        m = Menu(dish_id=add_form.dish.data, menu_price=add_form.price.data)
        try:
            db.session.add(m)
            db.session.commit()
            flash('ПОзиция меню сохранена!')
        except Exception as e:
            flash(f'Adding error: {e}')
        return redirect(url_for('.index'))

    return render_template("menu/index.html",
                           title='Меню',
                           data=query.all(),
                           query_form=f,
                           table_name='Меню',
                           add_form=add_form)


@bp.route('/del/<int:id>')
@login_required
def delete(id):
    if cuser.isnt_admin:  return redirect(url_for('index'))
    m = Menu.query.get_or_404(id)
    try:
        db.session.delete(m)
        db.session.commit()
    except Exception as e:
        flash(f'Нельзя')
    return redirect(url_for('.index'))


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    m = db.session.query(Menu).filter(Menu.menu_id == id).join(Dish).first()
    f = EditPriceForm(price=m.menu_price)
    if f.validate_on_submit():
        m.menu_price = f.price.data
        try:
            db.session.commit()
        except Exception as e:
            flash(f'Updating error: {e}')
        return redirect(url_for('.index'))
    else:
        return render_template('form.html',
                               title=f'Изменить позицию: {m.dish.dish_label} от {m.created_at}',
                               form=f)