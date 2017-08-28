""".

!/usr/bin/env python

"""
# -*- coding: utf-8 -*-
import subprocess
import time
import json
import os
import time as TIME
from datetime import datetime, time
import requests
import config_main

# add route
subprocess.call(config_main.ROUTE_EXEC, shell=True)

# take time
NOW = int(TIME.time())
CURRENT_TIME = datetime.now().time()
print NOW

# for demo purposes we will delete all the previous record 
for filerecorded in os.listdir('/home/records/'):
    os.unlink('/home/records/{}'.format(filerecorded))

# open json file to read client id
with open('/data/conf.json') as json_data_file:
    # read json info from file
    DATA = json.load(json_data_file)

    if DATA['registered']:
        REC_NAME = "c_{}_{}".format(str(DATA['registered']), str(NOW))
        
        print REC_NAME
        
        # start record
        subprocess.call("arecord -d 30 -f dat -c 1 /home/records/{}.wav".format(REC_NAME),
                        shell=True)
        subprocess.call("lame -r -s 48 -m m -b 64 /home/records/{}.wav /home/records/{}.mp3".format(REC_NAME, REC_NAME),
                        shell=True)
        subprocess.call("rm /home/records/{}.wav".format(REC_NAME), shell=True)
        
        # add file
        FILES = []
        FILES.append(('client_record', open("/home/records/{}.mp3".format(REC_NAME), 'rb')))

        #  send file to server by post request
        R = requests.post(config_main.URL,
                          files=FILES,
                          auth=('elio', '201092elio'),
                          timeout=15)

        print R.status_code 
