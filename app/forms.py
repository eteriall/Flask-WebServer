from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import PasswordField, BooleanField
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.validators import ValidationError, Email

from app.models import User




class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    """password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')])"""
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Аккаунт с таким именем уже существует.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Данная почта уже зарегистрирована.')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class EditProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    about_me = TextAreaField('Описание профиля', validators=[Length(min=0, max=140)])
    submit = SubmitField('Сохранить')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None and current_user.username != username.data:
            raise ValidationError('Аккаунт с таким именем уже существует.')


class PostForm(FlaskForm):
    post = TextAreaField('Напишите что-нибудь.', validators=[
        DataRequired(), Length(min=1, max=10000)])
    file = FileField()
    submit = SubmitField('Выложить')
