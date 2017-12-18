#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import os,json
from urllib.parse import urlparse
from pprint import pprint
import configparser 



# Define event callbacks
def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc))

def on_message(client, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

#def on_publish(client, obj, mid):
#    print("mid: " + str(mid))

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(client, obj, level, string):
    print(string)

mqttc = mqtt.Client()
# Assign event callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
#mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

# Mitsubishi and MQTT Params and Creds
# Import credentials, cause I don't want these on GIT :)
# Set if you do not use creds.py or would like to override
config = configparser.ConfigParser()
config.read("config.ini")
user = config.get("creds", "user")
password = config.get("creds", "password")
melview_endpoint = "https://api.melview.net"
mqqt_url_str = config.get("creds", "mqqt_url_str")

# Aircon Modes
heat = 1
dry = 2
cool = 3
fan = 7
auto = 8

# Uncomment to enable debug messages
#mqttc.on_log = on_log

url = urlparse(mqqt_url_str)

#topic = url.path[1:] or '/sensors/hvac_downstairs/current_temp'

# Get Mitshubisi Cookie
auth_cookie = os.popen('curl --insecure -H \"Accept: application/json, text/javascript, */*\" -X POST -d \'{\"user\":\"%s\",\"pass\":\"%s\",\"appversion\":\"3.2.673a\"}\' %s/api/login.aspx -i -s | grep Set-Cookie | awk -F \'Set-Cookie: \' \'{print $2}\' | awk -F\';\' \'{print $1}\'' % ( user, password, melview_endpoint )).read().rstrip("\n")
# Get aircon units
json_return = os.popen('curl --insecure -X GET -H \"Accept: application/json\" -H \"Cookie: %s\" %s/api/rooms.aspx?_=1513470690197 -s' % ( auth_cookie, melview_endpoint )).read().rstrip("\n")
unit_data = json.loads(json_return)

#Get downstairs unit state
unit_id = int(unit_data[0]["units"][1]["unitid"])

json_return = os.popen('curl --insecure -X GET -H \"Accept: application/json\" -H \"Cookie: %s\" -d \'{\"unitid\": %s, \"v\": 2}\' %s/api/unitcommand.aspx -s' % ( auth_cookie, unit_id, melview_endpoint )).read().rstrip("\n")

unit_state = json.loads(json_return)
#pprint(unit_state)

# Connect
mqttc.username_pw_set(url.username, url.password)
mqttc.connect(url.hostname, url.port)

# Start subscribe, with QoS level 0
#mqttc.subscribe(topic, 0)

# Publish a message
mqttc.publish('/sensors/hvac_downstairs/current_temp', int(unit_data[0]["units"][1]["temp"]))
mqttc.publish('/sensors/hvac_downstairs/temperature_state_topic', int(unit_data[0]["units"][1]["settemp"]))

if unit_state["setmode"] == auto:
  mqttc.publish('/sensors/hvac_downstairs/mode_state_topic', 'auto')
elif unit_state["setmode"] == cool:
  mqttc.publish('/sensors/hvac_downstairs/mode_state_topic', 'cool')
elif unit_state["setmode"] == heat:
  mqttc.publish('/sensors/hvac_downstairs/mode_state_topic', 'heat')
elif unit_state["setmode"] == dry:
  mqttc.publish('/sensors/hvac_downstairs/mode_state_topic', 'dry')
elif unit_state["setmode"] == fan_only:
  mqttc.publish('/sensors/hvac_downstairs/mode_state_topic', 'fan_only')