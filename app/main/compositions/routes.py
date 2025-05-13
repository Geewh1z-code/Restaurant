from flask import redirect, render_template, url_for, flash
from flask_login import current_user as cuser, login_required
from app import db
from app.main.compositions import bp
from app.models import Composition as Comp, DishCategory, Ingredient as Ingr, Unit, Dish, Store
from app.main.forms import EditValForm, FindSelForm, CompForm, FilterForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    f = FindSelForm()
    choices = [(0, 'All')]
    for d in Dish.query.all(): choices.append(d.to_touple())
    f.sel.choices = choices
    r = FilterForm()
    r.unit.choices = [unit.to_touple() for unit in Unit.query.all()]
    add_form = CompForm()
    add_form.dish.choices = [d.to_touple() for d in Dish.query.all()]
    add_form.ingr.choices = [i.to_touple() for i in Ingr.query.all()]
    query = db.session.query(Comp.comp_id, Comp.comp_val,
                             Comp.dish_id, Dish.dish_label,
                             Dish.dish_category_id, DishCategory.dish_category_label,
                             Comp.ingr_id, Ingr.ingr_label, Ingr.unit_id, Unit.unit_label) \
        .join(Dish, Comp.dish_id == Dish.dish_id) \
        .join(DishCategory, Dish.dish_category_id == DishCategory.dish_category_id) \
        .join(Ingr, Comp.ingr_id == Ingr.ingr_id).join(Unit)

    sstore = Store.query.order_by(Store.counted_at.desc()).distinct(Store.ingr_id).subquery()
    notif = db.session.query(Comp.ingr_id, Comp.comp_val, Ingr.unit_id, sstore.c.store_val) \
        .join(Ingr, Ingr.ingr_id == Comp.ingr_id).join(sstore, sstore.c.ingr_id == Comp.ingr_id)
    if f.submit.data and f.validate():
        sel = f.sel.data
        search = f.s.data
        if sel and sel != '0':
            query = query.filter(Dish.dish_id == sel)
        if search:
            query = query.filter(db.or_(Dish.dish_label.like(f'%{search}%'),
                                        DishCategory.dish_category_label.like(f'%{search}%'),
                                        Ingr.ingr_label.like(f'%{search}%')))
    elif r.submit1.data and r.validate():
        notif = notif.filter(Ingr.unit_id == r.unit.data, sstore.c.store_val <= r.val.data).subquery()
        query = query.join(notif, notif.c.ingr_id == Ingr.ingr_id).distinct(Comp.comp_id)
        print(query)
    elif add_form.validate_on_submit():
        r = Comp(dish_id=add_form.dish.data, ingr_id=add_form.ingr.data, comp_val=add_form.comp_val.data)
        try:
            db.session.add(r)
            db.session.commit()
            flash('Рецет добавлен!')
        except Exception as e:
            flash(f'Adding error: {e}')
        return redirect(url_for('.index'))

    return render_template("compositions/index.html",
                           title='Рецепты',
                           data=query.all(),
                           query_form=f,
                           filter_form=r,
                           table_name='Рецепты',
                           add_form=add_form)


@bp.route('/del/<int:id>')
@login_required
def delete(id):
    if cuser.isnt_admin:  return redirect(url_for('index'))
    c = Comp.query.get_or_404(id)
    try:
        db.session.delete(c)
        db.session.commit()
    except Exception as e:
        flash(f'Нельзя')
    return redirect(url_for('.index'))


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    c = db.session.query(Comp).filter(Comp.comp_id == id).join(Dish).join(Ingr).first()
    f = EditValForm(val=c.comp_val)
    if f.validate_on_submit():
        f.menu_price = f.val.data
        try:
            db.session.commit()
        except Exception as e:
            flash(f'Updating error: {e}')
        return redirect(url_for('.index'))
    else:
        return render_template('form.html',
                               title=f'Изменить количество: {c.dish.dish_label} / {c.ingr.ingr_label}',
                               form=f)
