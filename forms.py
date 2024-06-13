from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired

class StudentForm(FlaskForm):
    section = SelectField('Section', coerce=str, validators=[DataRequired()])
    competition = BooleanField('Competition')
    submit = SubmitField('Add Student')

class SectionForm(FlaskForm):
    name = StringField('Section Name', validators=[DataRequired()])
    monday = StringField('Monday', validators=[DataRequired()])
    tuesday = StringField('Tuesday', validators=[DataRequired()])
    wednesday = StringField('Wednesday', validators=[DataRequired()])
    thursday = StringField('Thursday', validators=[DataRequired()])
    friday = StringField('Friday', validators=[DataRequired()])
    saturday = StringField('Saturday', validators=[DataRequired()])
    sunday = StringField('Sunday', validators=[DataRequired()])
    submit = SubmitField('Add Section')

class LoginForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    role = SelectField('Role', choices=[('student', 'Student'), ('coach', 'Coach')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')
