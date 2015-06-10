# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import (BooleanField, DateField, FloatField, StringField, IntegerField,
                     DateTimeField, PasswordField, SelectField, TextAreaField, SelectMultipleField)
from wtforms import widgets
from wtforms.validators import DataRequired, InputRequired


class LoginForm(Form):
    username = StringField(validators=[InputRequired()])
    password = PasswordField(validators=[InputRequired()])
    remember_me = BooleanField()
