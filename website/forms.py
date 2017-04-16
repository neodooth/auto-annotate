# coding: utf8

__author__ = 'neodooth'

from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

class SigninForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])