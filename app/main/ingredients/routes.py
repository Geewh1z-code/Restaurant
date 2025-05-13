from flask import redirect, render_template, url_for, flash
from flask_login import current_user as cuser, login_required
from app import db
from app.main.ingredients import bp
from app.models import Ingredient, Store, Unit
from app.main.forms import FindForm, IngrForm, EditIngrForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if not cuser.is_admin:  return redirect(url_for('index'))
    f = FindForm()
    add_form = IngrForm()
    add_form.unit.choices = [unit.to_touple() for unit in Unit.query.all()]
    query = db.session.query(Ingredient.ingr_id, Ingredient.ingr_label, Unit.unit_label).join(Unit)
    if f.submit.data and f.validate():
        search = f.s.data
        if search:
            query = query.filter(db.or_(Ingredient.ingr_label.like(f'%{search}%'),
                                        Unit.unit_label.like(f'{search}')))
    elif add_form.validate_on_submit():
        ingr = Ingredient(ingr_label=add_form.label.data, unit_id=add_form.unit.data)
        try:
            db.session.add(ingr)
            db.session.commit()
            store = Store(ingr_id=ingr.ingr_id)
            db.session.add(store)
            db.session.commit()
            flash('Ингредиент сохранен!')
        except Exception as e:
            flash(f'Adding error: {e}')
        return redirect(url_for('.index'))
    return render_template("ingredients/index.html",
                           title='Ингредиенты',
                           table_name='Ингредиенты',
                           data=query.all(),
                           query_form=f,
                           add_form=add_form)


@bp.route('/del/<int:id>')
@login_required
def delete(id):
    if cuser.isnt_admin:  return redirect(url_for('index'))
    ingr = Ingredient.query.get_or_404(id)
    try:
        db.session.delete(ingr)
        db.session.commit()
    except Exception as e:
        flash(f'Нельзя')
    return redirect(url_for('.index'))


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if not cuser.is_admin:  return redirect(url_for('index'))
    ingr = Ingredient.query.get_or_404(id)
    f = EditIngrForm(old=ingr.ingr_label, label=ingr.ingr_label, unit=ingr.unit_id)
    f.unit.choices = [unit.to_touple() for unit in Unit.query.all()]
    if f.validate_on_submit():
        ingr.ingr_label = f.label.data
        ingr.unit_id = f.unit.data
        try:
            db.session.commit()
        except Exception as e:
            flash(f'Updating error: {e}')
        return redirect(url_for('.index'))
    else:
        return render_template('form.html', title='Изменить ингредиент', form=f)
