"""
    script to handle mqt connection
    for client updates
"""
import paho.mqtt.client as mqtt

SUB_ADMIN = 'Admin'
SUB_USER = 'Client'
URL = 'localhost'
USER_NAME = 'sammy'
PASSWORD = '201092' 

def on_connect(client, userdata, flags, rc):
    """
        The callback for when the client receives a CONNACK response from the server.
    """
    print "Connected with result code "+str(rc)

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(SUB_ADMIN)
    client.subscribe(SUB_USER)

def on_message(client, userdata, msg):
    """
        The callback for when a PUBLISH message is received from the server.
    """
    print msg.topic+" "+str(msg.payload)

# initialize client
CLIENT = mqtt.Client()
CLIENT.username_pw_set(USER_NAME, password=PASSWORD)

# set on message callback
CLIENT.on_message = on_message
CLIENT.on_connect = on_connect

# connect and subscribe
CLIENT.connect(URL, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
CLIENT.loop_forever(timeout=1.0, max_packets=1, retry_first_connection=False)
