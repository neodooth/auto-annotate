# coding: utf8

__author__ = 'neodooth'

from flask import Flask, Blueprint
from config import _IMAGE_ROOT


app = Flask(__name__)
app.config.from_object('config')

bp = Blueprint('data', '__main__', static_folder=_IMAGE_ROOT, url_prefix='')
app.register_blueprint(bp)

from website import views

import transmitter
transmitter.start_worker()