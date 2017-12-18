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



#topic = url.path[1:] or '/sensors/hvac_downstairs/current_temp'

# Get Mitshubisi Cookie
curl_cmd ='curl --insecure -H \"Accept: application/json, text/javascript, */*\" -X POST -d \'{\"user\":\"%s\",\"pass\":\"%s\",\"appversion\":\"3.2.673a\"}\' %s/api/login.aspx -i -s | grep Set-Cookie | awk -F \'Set-Cookie: \' \'{print $2}\' | awk -F\';\' \'{print $1}\'' % ( user, password, melview_endpoint )
auth_cookie = os.popen(curl_cmd).read().rstrip("\n")

# Get aircon units
curl_cmd = 'curl --insecure -X GET -H \"Accept: application/json\" -H \"Cookie: %s\" %s/api/rooms.aspx?_=1513470690197 -s' % ( auth_cookie, melview_endpoint )
json_return = os.popen(curl_cmd).read().rstrip("\n")
unit_data = json.loads(json_return)

# Count the number of airconditioners
unit_count = len(unit_data[0]["units"])

#G Get the states for aeach unit
unit_state = []
for unit_num in range(0, unit_count, 1):
    unit_id = int(unit_data[0]["units"][unit_num]["unitid"])
    curl_cmd = 'curl --insecure -X GET -H \"Accept: application/json\" -H \"Cookie: %s\" -d \'{\"unitid\": %s, \"v\": 2}\' %s/api/unitcommand.aspx -s' % ( auth_cookie, unit_id, melview_endpoint )
    json_return = os.popen(curl_cmd).read().rstrip("\n")
    unit_state.append(json.loads(json_return))

# Connect to MQTT, I'm using CloudMQTT but this will work using mosquito 
# Uncomment to enable debug messages.
#mqttc.on_log = on_log
url = urlparse(mqqt_url_str)
mqttc.username_pw_set(url.username, url.password)
mqttc.connect(url.hostname, url.port)


for unit_num in range(0, unit_count, 1):
    unit_name = unit_data[0]["units"][unit_num]["room"].lower()
# Publish stes for each unit to MQTT
    mqttc.publish('/sensors_hvac/%s/current_temp' % unit_name, int(unit_data[0]["units"][unit_num]["temp"]))
    mqttc.publish('/sensors_hvac/%s/temperature_state_topic' % unit_name, int(unit_data[0]["units"][unit_num]["settemp"]))
    if unit_state[unit_num]["setmode"] == auto:
      mqttc.publish('/sensors_hvac/%s/mode_state_topic' % unit_name, 'auto')
    elif unit_state[unit_num]["setmode"] == cool:
      mqttc.publish('/sensors_hvac/%s/mode_state_topic' % unit_name, 'cool')
    elif unit_state[unit_num]["setmode"] == heat:
      mqttc.publish('/sensors_hvac/%s/mode_state_topic' % unit_name, 'heat')
    elif unit_state[unit_num]["setmode"] == dry:
      mqttc.publish('/sensors_hvac/%s/mode_state_topic' % unit_name, 'dry')
    elif unit_state[unit_num]["setmode"] == fan_only:
      mqttc.publish('/sensors_hvac/%s/mode_state_topic' % unit_name, 'fan_only')
      
      
      
      
      
mqttc.diconnect()      