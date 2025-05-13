from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class AdmRegistrationForm(FlaskForm):
    old_username = HiddenField('Old')
    username = StringField('Логин', validators=[DataRequired()])
    fullname = StringField('ФИО', validators=[DataRequired()])
    old_email = HiddenField('Email old')
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль')
    password2 = PasswordField('Повторите пароль', validators=[EqualTo('password')])
    role = SelectField('Должность')
    submit = SubmitField('Сохранить')

    def validate_username(self, username):
        if self.old_username.data is None or (username.data != self.old_username.data):
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Выберите другой ник.')

    def validate_email(self, email):
        if self.old_email.data is None or (email.data != self.old_email.data):
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Выберите другой email.')