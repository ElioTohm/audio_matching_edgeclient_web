# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import getopt
import sys
import types

import iwconfig
import iwlist

import errno

from wifi import Cell, Scheme
# import pythonwifi.flags
# from pythonwifi.iwlibs import Wireless, Iwrange, getNICnames

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


@app.route('/')
def show_entries():
	wifi = Wireless('wlan0')
	Essid = wifi.getEssid()
	Mode = wifi.getMode()
	return render_template('helloworld.html', message=Essid)

@app.route('/search', methods=['GET'])
def search():
	return render_template('helloworld.html', message=Cell.all('wlan0'))

@app.route('/connect', methods=['GET'])
def connect():
	cell = Cell.all('wlan0')[0]
	scheme = Scheme.for_cell('wlan0', 'home', cell, passkey)
	scheme.save()
	scheme.activate()
	return render_template('helloworld.html', message='done')
