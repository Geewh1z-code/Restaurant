from flask import redirect, render_template, url_for, flash
from flask_login import current_user as cuser, login_required
from app import db
from app.main.vendors import bp
from app.models import Vendor
from app.main.forms import FindForm, AddForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if not cuser.is_admin:  return redirect(url_for('index'))
    f = FindForm()
    add_form = AddForm(item='vendor')
    query = Vendor.query
    if f.submit.data and f.validate():
        search = f.s.data
        if search:
            query = query.filter(Vendor.vendor_label.like(f'%{search}%'))
    elif add_form.validate_on_submit():
        vendor = Vendor(vendor_label=add_form.label.data)
        try:
            db.session.add(vendor)
            db.session.commit()
            flash('Поставщик сохранен!')
        except Exception as e:
            flash(f'Adding error: {e}')
        add_form.label.data = None
    return render_template("vendors/index.html",
                           title='Поставщики',
                           table_name='Поставщики ресторана',
                           data=query.all(),
                           query_form=f,
                           add_form=add_form)


@bp.route('/del/<int:id>')
@login_required
def delete(id):
    if cuser.isnt_admin:  return redirect(url_for('index'))
    vendor = Vendor.query.get_or_404(id)
    try:
        db.session.delete(vendor)
        db.session.commit()
    except Exception as e:
        flash(f'Нельзя')
    return redirect(url_for('.index'))
