from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, Email, NumberRange

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")


class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Reset Instructions")

class ScanForm(FlaskForm):
    target = StringField("Target (URL or IP)", validators=[DataRequired(), Length(min=3)])
    submit = SubmitField("Start Scan")


class AdminLoginForm(FlaskForm):
    username = StringField("Admin Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    favorite_color = StringField("Favorite color", validators=[DataRequired(), Length(min=2, max=30)])
    age = IntegerField("Age", validators=[DataRequired(), NumberRange(min=1, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Admin Login")
