"""
flaskr app to help technician connect set up register device
using mqt to connect users to broker
"""
import os
import json
import subprocess
import iwlist
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import requests
from pythonwifi.iwlibs import Wireless
import paho.mqtt.client as mqtt
import config

APP = Flask(__name__) # create the application instance :)
APP.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
APP.config.update(dict(
    DATABASE=os.path.join(APP.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='PM@#12345'
))
APP.config.from_envvar('FLASKR_SETTINGS', silent=True)


@APP.route('/')
def show_entries():
    """
    show wifi entries
    """
    wifi = Wireless('wlan0')
    essid = wifi.getEssid()
    return render_template('home.html', message=essid)

@APP.route('/search', methods=['GET'])
def search():
    """
    search for wifi signal near the device
    """
    return render_template('connect.html', SSIDs=iwlist.scan_wifi())

@APP.route('/connect', methods=['Post'])
def connect():
    """
    connect to the wifi
    """
    subprocess.call(["nmcli", "dev", "wifi", "connect",
                     request.form['SSID'], "password", request.form['pwd']])
    return render_template('connect.html')

@APP.route('/connect', methods=['GET'])
def show_connect():
    """
    show page to browse and connect wifi available
    """
    return render_template('connect.html')

@APP.route('/login', methods=['GET', 'POST'])
def login():
    """
    on post login user
    on get show data if the user is logged in
    """
    if request.method == 'POST':
        if request.form['username'] == APP.config['USERNAME']:
            flash('Invalid username')
        elif request.form['password'] != APP.config['PASSWORD']:
            flash('Invalid password')
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('connect.html')


@APP.route('/logout', methods=['GET'])
def logout():
    """
    Get to logout and hide sensitive data from unauthorized users
    """
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@APP.route('/register', methods=['GET', 'POST'])
def show_register():
    """
    on get show registration page
    on post Register client and save response to json file
    """
    if request.method == 'POST':
        headers = {'content-type': 'application/json'}

        data = {"long": request.form['long'], "lat": request.form['lat'],
                "name": request.form['name']}

        request_result = requests.post(config.REGISTER_URL, auth=('elio', '201092elio'),
                                       data=json.dumps(data),
                                       headers=headers,
                                       timeout=15)

        if request_result.json()['location']:
            result = {'registered': int(request_result.json()['registered']),
                      'long': request_result.json()['long'], 'lat': request_result.json()['lat']}
        else:
            result = {'registered': int(request_result.json()['registered']),
                      'version': float(request_result.json()['version'])}

        with open(config.JSON_CONFIG, 'w') as outfile:
            json.dump(result, outfile)

        with open('/etc/NetworkManager/system-connections/vpn-PMvpn', 'a+') as file:
            file.write('user=PM'+str(request_result.json()['registered'])+'\n')

        return render_template('register.html',
                               client=request_result.json()['registered'], isregisterd=True)
    else:
        if os.path.isfile(config.JSON_CONFIG):
            # get current directory
            if os.stat(config.JSON_CONFIG).st_size == 0:
                return render_template('register.html', isregisterd=False)
            else:
                client = ''
                with open(config.JSON_CONFIG) as client_data_file:
                    client = json.load(client_data_file)
                return render_template('register.html',
                                       isregisterd=True, client=client['registered'])
        else:
            file = open(config.JSON_CONFIG, 'w+')
            return render_template('register.html', isregisterd=False)


@APP.route('/save', methods=['GET'])
def savechanges():
    """
    reboot device to save files written
    """
    subprocess.call(['reboot'])

def on_connect(client, userdata, flags, rc):
    """
    The callback for when the client receives a CONNACK response from the server.
    """
    print "Connected with result code {} ".format(str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(config.SUB_ADMIN)
    client.subscribe(config.SUB_USER)

def on_message(client, userdata, msg):
    """
    The callback for when a PUBLISH message is received from the server.
    """
    print "{} {}".format(msg.topic, str(msg.payload))
    version = read_confjs('version')
    message = json.loads(msg.payload)
    if version > float(message['version']):
        process = subprocess.Popen(["git", "pull", config.GIT_REPO], stdout=subprocess.PIPE)
        output = process.communicate()[0]

        client_id = read_confjs('registered')
        result = {'registered': client_id, 'version': float(message['version'])}
        with open(config.JSON_CONFIG, 'w') as outfile:
            json.dump(result, outfile)

        print output
        subprocess.Popen(['reboot'])


def read_confjs(key):
    """
    check if device is registerer by reading the informations in the conf.js file
    """
    if os.stat(config.JSON_CONFIG).st_size > 0:
        with open(config.JSON_CONFIG) as client_data_file:
            keyvalue = json.load(client_data_file)
            keyvalue = keyvalue[key]
            return str(keyvalue)

def start_mqtt_subscribtion():
    """
    start mqt subsctiption if the device has
    @CLIENT_ID IOW is registered
    """
    client_id = read_confjs('registered')
    if client_id != None:
        # initialize client
        mqttc = mqtt.Client(client_id=client_id, clean_session=False)
        mqttc.username_pw_set(config.USER_NAME, password=config.PASSWORD)

        # set on message callback
        mqttc.on_message = on_message
        mqttc.on_connect = on_connect

        # connect and subscribe
        mqttc.connect_async(config.URL, 1883)
        mqttc.loop_start()

start_mqtt_subscribtion()

APP.run(host=config.FLASKR_HOST, port=config.FLASKR_PORT)
