#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import os,json
from urllib.parse import urlparse
from pprint import pprint
import configparser 
import requests


# Define event callbacks
def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc))

# Handle incoming MQQT message and translate
def on_message(client, obj, msg):
    # print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    # Break out the command and topic from the MQQT topic
    topic = msg.topic.split("/")
    unit_name= topic[2]
    command = topic[3]
    print(command)
    if command == 'mode_command_topic':
        mode = aircon_modes.index(msg.payload.decode('ascii'))
        mqttc.publish('/sensors_hvac/%s/mode_state_topic' % unit_name, aircon_modes[unit_state[unit_num]["setmode"]])


#def on_publish(client, obj, mid):
#    print("mid: " + str(mid))

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(client, obj, level, string):
    print(string)

mqttc = mqtt.Client()
# Assign event callbacks
mqttc.on_message = on_message
#mqttc.on_connect = on_connect
#mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

# Mitsubishi and MQTT Params and Creds
# Import credentials, cause I don't want these on GIT :)
# Set if you do not use creds.py or would like to override
config = configparser.ConfigParser()
config.read("config.ini")
user = config.get("creds", "user")
password = config.get("creds", "password")
mqqt_url_str = config.get("creds", "mqqt_url_str")
melview_endpoint = "https://api.melview.net"

# Aircon Modes
# See what I did here :)
aircon_modes = ['0','heat','dry','cool','4','5','6','fan_only','auto']
aircon_fanspeeds = ['auto','low','low','medium','medium','high','high']
aircon_airdir = ['off','off','off','off','off','off','off','on']
aircon_power = ['off','on']

# Get Mitshubisi Cookie
headers = {'Accept': 'application/json, text/javascript, */*'}
payload = {'user': user, 'pass': password, 'appversion': '3.2.673a'}
r = requests.post("%s/api/login.aspx" % melview_endpoint, headers=headers, data=json.dumps(payload))
if r.status_code != 200:
    print("ERROR: Melview endpoint HTTP error code %s" % r.status_code )

# Get aircon units
auth_cookie = r.headers.get('Set-cookie')
headers = {'Accept': 'application/json, text/javascript, */*', 'Cookie': auth_cookie }
r = requests.post("%s/api/rooms.aspx?_=1513470690197" % melview_endpoint, headers=headers)
json_format = json.loads(r.text)
unit_data = json_format[0]
# Count the number of airconditioners
unit_count = len(unit_data["units"])

# Get the states for each unit
unit_state = []
for unit_num in range(0, unit_count, 1):
    unit_id = int(unit_data["units"][unit_num]["unitid"])
    payload = {'unitid': unit_id, 'v': '2'}
    r = requests.post("%s/api/unitcommand.aspx" % melview_endpoint, headers=headers, data=json.dumps(payload))
    json_return = r.text
    unit_state.append(json.loads(json_return))

# Connect to MQTT, I'm using CloudMQTT but this will work using mosquito 
# Uncomment to enable debug messages.
#mqttc.on_log = on_log
url = urlparse(mqqt_url_str)
mqttc.username_pw_set(url.username, url.password)
mqttc.connect(url.hostname, url.port)

# Subscript to the HVAC topic
#mqttc.subscribe([("/sensors_hvac/lounge/mode_command_topic", 0),("/sensors_hvac/downstairs/mode_command_topic", 0),("/sensors_hvac/lounge/target_temp", 0),("/sensors_hvac/downstairs/target_temp", 0)])

# Iterate through the json list and publish each key/value pair to a topic.
for unit_num in range(0, unit_count, 1):
    unit_name = unit_data["units"][unit_num]["room"].lower()
# Publish states for each unit to MQTT
    for key, value in unit_state[unit_num].items():
        if key == 'setmode':
            value = aircon_modes[value]
        if key == 'setfan':
            value = aircon_fanspeeds[value]
        if key == 'airdir':
            value = aircon_airdir[value]
        if key == 'power':
            value = aircon_power[value]
        mqttc.publish('/sensors_hvac/%s/%s' % (unit_name, key), value)
      
#mqttc.loop_forever()      
mqttc.disconnect() 
   