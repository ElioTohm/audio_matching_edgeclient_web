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

import pythonwifi.flags
from pythonwifi.iwlibs import Wireless, Iwrange, getNICnames
from subprocess import call


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
	return render_template('home.html', message=Essid)

@app.route('/search', methods=['GET'])
def search():
	return render_template('connect.html', SSIDs=iwlist.scan_wifi())

@app.route('/connect', methods=['Post'])
def connect():
	call(["nmcli", "dev", "wifi", "connect", request.form['SSID'], "password", request.form['pwd']])
	return render_template('connect.html')

@app.route('/connect', methods=['GET'])
def show_connect():
	return render_template('connect.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))