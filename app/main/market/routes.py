from flask import redirect, render_template, url_for, flash
from flask_login import current_user as cuser, login_required
from app import db
from app.main.market import bp
from app.models import Ingredient, Unit, Vendor, Market
from app.main.forms import FindForm, MarketForm, EditPriceForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if not cuser.has_role('supplier'):  return redirect(url_for('index'))
    f = FindForm()
    add_form = MarketForm()
    add_form.ingr.choices = [ingr.to_touple() for ingr in Ingredient.query.all()]
    add_form.vendor.choices = [vendor.to_touple() for vendor in Vendor.query.all()]
    query = db.session.query(Market.ingr_price, Market.vendor_id, Vendor.vendor_label,
                             Market.ingr_id, Ingredient.ingr_label, Ingredient.unit_id,
                             Unit.unit_label).join(Vendor).join(Ingredient).join(Unit)
    if f.submit.data and f.validate():
        search = f.s.data
        if search:
            query = query.filter(db.or_(Ingredient.ingr_label.like(f'%{search}%'),
                                        Unit.unit_label.like(f'{search}'),
                                        Vendor.vendor_label.like(f'%{search}%'))) \
                .order_by(Market.ingr_price)
    elif add_form.validate_on_submit():
        ingr = Ingredient.query.get_or_404(add_form.ingr.data)
        vendor = Vendor.query.get_or_404(add_form.vendor.data)
        market = Market(ingr_id=add_form.ingr.data, vendor_id=add_form.vendor.data, ingr_price=add_form.price.data)
        ingr.market.append(market)
        vendor.market.append(market)
        try:
            db.session.commit()
            flash('Позиция сохранена!')
        except Exception as e:
            flash(f'Adding error: {e}')
        return redirect(url_for('.index'))
    return render_template("market/index.html",
                           title='Поставки',
                           table_name='Предложение поставок',
                           data=query.all(),
                           query_form=f,
                           add_form=add_form)


@bp.route('/del/<int:vendor_id>/<int:ingr_id>')
@login_required
def delete(vendor_id, ingr_id):
    if cuser.isnt_admin:  return redirect(url_for('index'))
    market = Market.query.filter_by(ingr_id=ingr_id, vendor_id=vendor_id).first()
    try:
        db.session.delete(market)
        db.session.commit()
    except Exception as e:
        flash(f'Нельзя')
    return redirect(url_for('.index'))


@bp.route('/edit<int:vendor_id>/<int:ingr_id>', methods=['GET', 'POST'])
@login_required
def edit(vendor_id, ingr_id):
    if not cuser.is_admin:  return redirect(url_for('index'))
    offer = Market.query.filter_by(ingr_id=ingr_id, vendor_id=vendor_id) \
        .join(Vendor).join(Ingredient).first()
    f = EditPriceForm(price=offer.ingr_price)
    if f.validate_on_submit():
        offer.ingr_price = f.price.data
        try:
            db.session.commit()
        except Exception as e:
            flash(f'Updating error: {e}')
        return redirect(url_for('.index'))
    else:
        return render_template('form.html',
                               title=f'Изменить предложение: {offer.ingredient.ingr_label} от {offer.vendor.vendor_label}',
                               form=f)