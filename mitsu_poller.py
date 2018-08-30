#!/usr/bin/env python3
# This script polls the Mitsubishi Service for the current units associated with the acocunt and then queries the unit data.
# All data is then transformed and pushed to MQTT
import paho.mqtt.client as mqtt
import os,json
from urllib.parse import urlparse
from pprint import pprint
import configparser 
import requests
import logging

logging.basicConfig(filename="mitsu_poller.log",level=logging.DEBUG,format='%(asctime)s - %(name)s - %(threadName)s - %(message)s')

# Mitsubishi Functions
def mitsu_getcookie():
    headers = {'Accept': 'application/json, text/javascript, */*'}
    payload = {'user': user, 'pass': password, 'appversion': '3.3.838'}
    r = requests.post("%s/api/login.aspx" % melview_endpoint, headers=headers, data=json.dumps(payload))
    logging.debug("logged in")
    return r.headers.get('Set-cookie')

def mitsu_getunits():
    r = requests.post("%s/api/rooms.aspx?_=1513470690197" % melview_endpoint, headers=headers)
    json_format = json.loads(r.text)
    logging.debug("got unit info: " + r.text)
    return json_format[0]

def mitsu_getstates():
    unit_state = []
    for unit_num in range(0, unit_count, 1):
        unit_id = int(unit_data["units"][unit_num]["unitid"])
        payload = {'unitid': unit_id, "v": 3}
        r = requests.post("%s/api/unitcommand.aspx" % melview_endpoint, headers=headers, data=json.dumps(payload))
        json_return = r.text
        unit_state.append(json.loads(json_return))
        logging.debug("got state info: " + r.text)
    return unit_state

def mitsu_senddata(datadict):       
    for key, value in datadict.items():
        if key == 'setmode':
            if datadict['power'] == 1:
                value = aircon_modes[value]
            else:
                value = aircon_modes[9]
        if key == 'setfan':
            value = aircon_fanspeeds[value]
        if key == 'airdir':
            value = aircon_airdir[value]
        mqttc.publish('/sensors_hvac/%s/%s' % (unit_name, key), value)
        logging.debug("mqtt publish: sensors_hvac/" + unit_name + "/" + key + " value = " + str(value))
# Define event callbacks
def on_connect(client, userdata, flags, rc):
    logging.debug("rc: " + str(rc))

# Handle incoming MQQT message and translate
def on_message(client, obj, msg):
     logging.debug(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    # Break out the command and topic from the MQQT topic

#def on_publish(client, obj, mid):
#    print("mid: " + str(mid))

def on_subscribe(client, obj, mid, granted_qos):
    logging.debug("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(client, obj, level, string):
    logging.debug(string)

mqttc = mqtt.Client()
# Assign event callbacks
mqttc.on_message = on_message
#mqttc.on_connect = on_connect
#mqttc.on_publish = on_publish
#mqttc.on_subscribe = on_subscribe
mqttc.on_log = on_log

# Mitsubishi and MQTT Params and Creds
# Import credentials, cause I don't want these on GIT :)
# Set if you do not use creds.py or would like to override
config = configparser.ConfigParser()
config.read("config.ini")
user = config.get("creds", "user")
password = config.get("creds", "password")
mqqt_url_str = config.get("creds", "mqqt_url_str")
melview_endpoint = "https://api.melview.net"

# Mitsubishi comman code translation
mitsu_command_codes = {"setfan":"FS", "airdir":"AV", "setmode":"PW1,MD", "power":"PW"}
# Mapping values (Mitsubishi) to command words (HA)
aircon_modes = ['0','heat','dry','cool','4','5','6','fan_only','auto','off']
aircon_fanspeeds = ['auto','low','low','medium','medium','high','high']
aircon_airdir = ['off','off','off','off','off','off','off','on']
# Mapping words (HA) to command values (Mitsubishi)
aircon_cairdir = {"off":3,"on":7}
aircon_cfanspeed = {"auto":"0","low":"1","medium":"4","high":"6"}



# Get Mitshubisi Cookie
auth_cookie = mitsu_getcookie()
headers = {'Accept': 'application/json, text/javascript, */*', 'Cookie': auth_cookie }

# Get aircon units
unit_data = mitsu_getunits()
# Count the number of airconditioners
unit_count = len(unit_data["units"])
# Get the states for each unit
unit_state =  mitsu_getstates()


# Connect to MQTT, I'm using CloudMQTT but this will work using mosquito 
url = urlparse(mqqt_url_str)
mqttc.username_pw_set(url.username, url.password)
mqttc.connect(url.hostname, url.port)

# Subscript to the HVAC topic
#mqttc.subscribe([("/sensors_hvac/lounge/mode_command_topic", 0),("/sensors_hvac/downstairs/mode_command_topic", 0),("/sensors_hvac/lounge/target_temp", 0),("/sensors_hvac/downstairs/target_temp", 0)])

# Iterate through the json list and publish each key/value pair to a topic.
for unit_num in range(0, unit_count, 1):
    unit_name = unit_data["units"][unit_num]["room"].lower()
    # Publish states for each unit to MQTT
    mitsu_senddata(unit_state[unit_num])

    
mqttc.disconnect() 
   
