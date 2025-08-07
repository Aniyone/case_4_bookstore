from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange

class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class BookForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    author = StringField('Автор', validators=[DataRequired()])
    category = StringField('Категория', validators=[DataRequired()])
    year = IntegerField('Год выхода', validators=[NumberRange(min=0)])
    price = FloatField('Цена', validators=[DataRequired()])
    available = BooleanField('Статус')
    submit = SubmitField('Обновить книгу')

class RentalForm(FlaskForm):
    duration = SelectField('Rental Duration', choices=[
        ('14', '2 Weeks'),
        ('30', '1 Month'),
        ('90', '3 Months')
    ])
    submit = SubmitField('Rent Book')
