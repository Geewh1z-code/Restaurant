from datetime import datetime
from flask import redirect, render_template, url_for, flash
from flask_login import current_user as cuser, login_required
from app import db
from app.main.waybills import bp
from app.models import Ingredient, Store, Unit, Vendor, Waybill, User
from app.main.forms import FindTimeForm, WaybillForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if not cuser.has_role('supplier'):  return redirect(url_for('index'))
    f = FindTimeForm()
    query = db.session.query(Waybill.waybill_id, Waybill.waybill_val, Waybill.recd_at,
                             Waybill.vendor_id, Vendor.vendor_label, Waybill.user_id, User.user_fullname,
                             Waybill.ingr_id, Ingredient.ingr_label, Ingredient.unit_id,
                             Unit.unit_label).join(User).join(Vendor).join(Ingredient).join(Unit)
    if f.validate_on_submit():
        search = f.s.data
        start = f.start.data
        end = f.until.data
        if search:
            query = query.filter(db.or_(Ingredient.ingr_label.like(f'%{search}%'),
                                        User.user_fullname.like(f'%{search}%'),
                                        Vendor.vendor_label.like(f'%{search}%')))
        if start:
            query = query.filter(Waybill.recd_at >= start)
        if end:
            query = query.filter(Waybill.recd_at <= end)
    return render_template("waybills/index.html",
                           title='Накладные',
                           table_name='Накладные',
                           data=query.all(),
                           query_form=f)


@bp.route('/add/<int:vendor_id>/<int:ingr_id>', methods=['GET', 'POST'])
@login_required
def add(vendor_id, ingr_id):
    if not cuser.has_role('supplier'):  return redirect(url_for('index'))
    today = datetime.now().strftime('%Y-%m-%d')
    f = WaybillForm()
    f.ingr.choices = [Ingredient.query.get_or_404(ingr_id).to_touple()]
    f.vendor.choices = [Vendor.query.get_or_404(vendor_id).to_touple()]
    f.supplier.choices = [cuser.to_touple()]

    if f.validate_on_submit():
        wb = Waybill(ingr_id=f.ingr.data, vendor_id=f.vendor.data,
                     user_id=f.supplier.data, waybill_val=f.waybill_val.data)
        store = Store.query.filter(Store.ingr_id == f.ingr.data).order_by(Store.counted_at.desc()).first()
        if store.counted_at.strftime('%Y-%m-%d') == today:
            store.store_val = store.store_val + f.waybill_val.data
        else:
            nstore = Store(ingr_id=f.ingr.data, store_val=store.store_val + f.waybill_val.data)
            db.session.add(nstore)
        try:
            db.session.add(wb)
            db.session.commit()
            flash('Сохранено!')
        except Exception as e:
            flash(f'Add error: {e}')
        return redirect(url_for('.index'))
    return render_template('form.html', title='Добавить накладную', form=f)


@bp.route('/del/<int:id>')
@login_required
def delete(id):
    if not cuser.is_admin:  return redirect(url_for('index'))
    wb = Waybill.query.get_or_404(id)
    try:
        db.session.delete(wb)
        db.session.commit()
    except Exception as e:
        flash(f'нельзя')
    return redirect(url_for('.index'))


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if not cuser.is_admin:  return redirect(url_for('index'))
    wb = Waybill.query.filter_by(waybill_id=id).join(Vendor).join(User).join(Ingredient).join(Unit).first()
    f = WaybillForm(ingr=wb.ingr_id, vendor=wb.vendor_id,
                    supplier=wb.user_id, waybill_val=wb.waybill_val)
    f.ingr.choices = [ingr.to_touple() for ingr in Ingredient.query.all()]
    f.vendor.choices = [vendor.to_touple() for vendor in Vendor.query.all()]
    f.supplier.choices = [user.to_touple() for user in User.query.all()]
    if f.validate_on_submit():
        wb.ingr_id = f.ingr.data
        wb.vendor_id = f.vendor.data
        wb.user_id = f.supplier.data
        wb.waybill_val = f.waybill_val.data
        try:
            db.session.commit()
        except Exception as e:
            flash(f'{e}')
        return redirect(url_for('.index'))
    else:
        return render_template('form.html', title=f'изменить накладную', form=f)
