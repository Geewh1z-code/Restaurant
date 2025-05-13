from flask import redirect, render_template, url_for, flash
from flask_login import current_user as cuser, login_required
from app import db
from app.main.dishes import bp
from app.models import Dish, DishCategory
from app.main.forms import EditDishForm, FindForm, DishForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    f = FindForm()
    add_form = DishForm()
    add_form.cat.choices = [ctg.to_touple() for ctg in
                            DishCategory.query.order_by(DishCategory.dish_category_label).all()]
    query = db.session.query(Dish.dish_id, Dish.dish_label,
                             Dish.dish_category_id, DishCategory.dish_category_label) \
        .join(DishCategory)
    if f.submit.data and f.validate():
        search = f.s.data
        if search:
            query = query.filter(db.or_(Dish.dish_label.like(f'%{search}%'),
                                        DishCategory.dish_category_label.like(f'%{search}%')))
    elif add_form.validate_on_submit():
        dish = Dish(dish_label=add_form.label.data, dish_category_id=add_form.cat.data)
        try:
            db.session.add(dish)
            db.session.commit()
            flash('Блюдо добавлено!')
        except Exception as e:
            flash(f'Adding error: {e}')
        return redirect(url_for('.index'))
    return render_template("dishes/index.html",
                           title='Блюда',
                           data=query.all(),
                           query_form=f,
                           table_name='Блюда ресторана',
                           add_form=add_form)


@bp.route('/del/<int:id>')
@login_required
def delete(id):
    if cuser.isnt_admin:  return redirect(url_for('index'))
    dish = Dish.query.get_or_404(id)
    try:
        db.session.delete(dish)
        db.session.commit()
    except Exception as e:
        flash(f'Нельзя')
    return redirect(url_for('.index'))


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    dish = Dish.query.get_or_404(id)
    f = EditDishForm(old=dish.dish_label, label=dish.dish_label, cat=dish.dish_category_id)
    f.cat.choices = [ctg.to_touple() for ctg in DishCategory.query.order_by(DishCategory.dish_category_label).all()]
    if f.validate_on_submit():
        dish.dish_label = f.label.data
        dish.dish_category_id = f.cat.data
        try:
            db.session.commit()
        except Exception as e:
            flash(f'Updating error: {e}')
        return redirect(url_for('.index'))
    else:
        return render_template('form.html', title='Изменить блюдо', form=f)

