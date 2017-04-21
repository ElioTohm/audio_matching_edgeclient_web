"""
    !/usr/bin/env python
"""
# -*- coding: utf-8 -*-
import subprocess
import time
import json
import os
import requests

# add route
subprocess.call('route add -net 1.1.1.0/24 dev ppp0', shell=True)

# the server URL
URL = 'http://cloudpm.ddns.net:45454/matching/match/'

# take time
NOW = int(time.time())

# open json file to read client id
with open('/home/conf.json') as json_data_file:
    # read json info from file
    DATA = json.load(json_data_file)

if DATA['registered']:

    # start record
    subprocess.call('arecord -d 30 -f dat -c 1 /home/records/c_' +
                    str(DATA['registered']) + '_'+str(NOW) + '.wav',
                    shell=True)
    subprocess.call('lame -r -s 48 -m m -b 64 /home/records/c_' +
                    str(DATA['registered'])+'_' + str(NOW) +
                    '.wav /home/records/c_' +
                    str(DATA['registered']) + '_' + str(NOW)+'.mp3',
                    shell=True)
    subprocess.call('rm /home/records/c_' + str(DATA['registered']) +
                    '_' + str(NOW) +
                    '.wav', shell=True)

    time.sleep(120)

    # add file
    FILES = []

    for filerecorded in os.listdir('/home/records/'):
        if filerecorded.endswith('.mp3'):
            FILES.append(('client_record', open('/home/records/' + filerecorded, 'rb')))

    #  send file to server by post request
    R = requests.post(URL,
                      files=FILES,
                      auth=('elio', '201092elio'),
                      timeout=15)

    if R.status_code == 200:
        for filerecorded in os.listdir('/home/records/'):
            if filerecorded.endswith('.mp3'):
                os.unlink('/home/records/' + filerecorded)
