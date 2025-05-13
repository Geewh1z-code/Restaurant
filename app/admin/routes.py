from flask import request, redirect, render_template, url_for, flash
from flask_login import current_user as cuser, login_required
from app import db
from app.admin import bp
from app.models import User, Role
from app.main.forms import FindTimeForm
from app.admin.forms import AdmRegistrationForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if not cuser.is_admin:
        return redirect(url_for('index'))
    q = FindTimeForm()
    query = User.query
    if q.validate_on_submit():
        search = q.q.data
        start = q.dt_start.data
        end = q.dt_end.data
        if search:
            query = query.filter(User.username.like(f'%{search}%'))
        if start:
            query = query.filter(User.created_at >= start)
        if end:
            query = query.filter(User.created_at <= end)
    return render_template("admin/index.html",
                           title='Персонал',
                           data=query.all(),
                           query_form=q,
                           table_name='Персонал',
                           add='admin.add')


@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    if not cuser.is_admin:  return redirect(url_for('index'))
    user = User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('.index'))
    except Exception as e:
        return f'Ошибка удаления: {e}'


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if not cuser.is_admin:  return redirect(url_for('index'))
    form = AdmRegistrationForm()
    form.role.choices = [role.to_touple() for role in Role.query.all()]
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    user_fullname=form.fullname.data)
        user.set_password(form.password.data)
        new_role = Role.query.get(form.role.data)
        user.roles = [new_role, ]
        db.session.add(user)
        db.session.commit()
        flash('Пользователь добавлен!')
        return redirect(url_for('.index'))
    return render_template('form.html', title='Зарегистрировать', form=form)


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if not cuser.is_admin:
        return redirect(url_for('index'))
    user = User.query.get_or_404(id)
    form = AdmRegistrationForm(username=user.username, email=user.email,
                               role=user.roles[0], old_username=user.username,
                               old_email=user.email, fullname=user.user_fullname)
    form.role.choices = [role.to_touple() for role in Role.query.all()]
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.user_fullname = form.fullname.data
        if form.password.data:
            user.set_password(form.password.data)
        new_role = Role.query.get(form.role.data)
        user.roles = [new_role, ]
        try:
            db.session.commit()
        except Exception as e:
            flash(f'Ошибка: {e}')
        return redirect(url_for('.index'))
    else:
        return render_template('form.html', title='Изменение аккаунта', form=form)
