# coding: utf8

__author__ = 'neodooth'

from flask import Flask

app = Flask(__name__)

from downloader import views

from downloader import worker, detector, transmitter
worker.start_worker()
detector.start_detector()
transmitter.start_transmitter()