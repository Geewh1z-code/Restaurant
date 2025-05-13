from flask import redirect, render_template, url_for, flash
from flask_login import current_user as cuser, login_required
from app import db
from app.main.dish_ctg import bp
from app.models import DishCategory
from app.main.forms import FindForm, AddForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if not cuser.is_admin:  return redirect(url_for('index'))
    f = FindForm()
    add_form = AddForm(item='category')
    query = DishCategory.query
    if f.submit.data and f.validate():
        search = f.s.data
        if search:
            query = query.filter(DishCategory.dish_category_label.like(f'%{search}%'))
    elif add_form.validate_on_submit():
        category = DishCategory(dish_category_label=add_form.label.data)
        try:
            db.session.add(category)
            db.session.commit()
            flash('Категория блюда добавлена!')
        except Exception as e:
            flash(f'Adding error: {e}')
        add_form.label.data = None
    return render_template("dish_ctg/index.html",
                           title='Категории',
                           table_name='Категории блюд',
                           data=query.all(),
                           query_form=f,
                           add_form=add_form)


@bp.route('/del/<int:id>')
@login_required
def delete(id):
    if cuser.isnt_admin:  return redirect(url_for('index'))
    category = DishCategory.query.get_or_404(id)
    try:
        db.session.delete(category)
        db.session.commit()
    except Exception as e:
        flash(f'Нельзя')
    return redirect(url_for('.index'))