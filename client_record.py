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
# open json file to read client id
with open('/data/conf.json') as json_data_file:
    # read json info from file
    DATA = json.load(json_data_file)

    if DATA['registered']:
        REC_NAME = "c_{}_{}".format(str(DATA['registered']), str(NOW))

        # for demo purposes we will delete all the previous record 
        for filerecorded in os.listdir('/home/records/'):
            if filerecorded.endswith('.mp3'):
                os.unlink('/home/records/{}'.format(filerecorded))

        # start record
        subprocess.call("arecord -d 5 -f dat -c 1 /home/records/{}.wav".format(REC_NAME),
                        shell=True)
        subprocess.call("lame -r -s 48 -m m -b 64 /home/records/{}.wav /home/records/{}.mp3".format(REC_NAME, REC_NAME),
                        shell=True)
        subprocess.call("rm /home/records/{}.wav".format(REC_NAME), shell=True)
        
        # add file
        FILES = []
        UNLINK_ALL = None

        if CURRENT_TIME >= time(2, 00) and CURRENT_TIME <= time(5, 00):
            UNLINK_ALL = True
            for filerecorded in os.listdir('/home/records/'):
                if filerecorded.endswith('.mp3'):
                    FILES.append(('client_record', open('/home/records/' + filerecorded, 'rb')))
        else:
            UNLINK_ALL = False
            FILES.append(('client_record', open("/home/records/{}.mp3".format(REC_NAME), 'rb')))


        #  send file to server by post request
        R = requests.post(config_main.URL,
                          files=FILES,
                          auth=('elio', '201092elio'),
                          timeout=15)

        if R.status_code == 200:
            if UNLINK_ALL:
                for filerecorded in os.listdir('/home/records/'):
                    if filerecorded.endswith('.mp3'):
                        os.unlink('/home/records/{}'.format(filerecorded))
            else:
                os.unlink("/home/records/{}.mp3".format(REC_NAME))
