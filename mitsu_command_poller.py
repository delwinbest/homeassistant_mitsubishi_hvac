#!/usr/bin/env python3
# This script should run as a service. 
# It will subscribe to the MQTT topics, and one revieving a command, post the command the the Mitsubishi service.
# WARNING: There is NO error handling in this script yet
import paho.mqtt.client as mqtt
import os, json
from urllib.parse import urlparse
from pprint import pprint
import configparser 
import requests


def createDaemon():
# This function create a service/Daemon
  try:
    # Store the Fork PID
    pid = os.fork()
    if pid > 0:
      print("PID: %d" % pid)
      os._exit(0)
  except OSError as error:
    print("Unable to fork. Error: %d (%s)" % (error.errno, error.strerror))
    os._exit(1)

  run_poller()
  
# Mitsubishi Functions
def mitsu_getcookie():
    headers = {'Accept': 'application/json, text/javascript, */*'}
    payload = {'user': user, 'pass': password, 'appversion': '3.2.673a'}
    r = requests.post("%s/api/login.aspx" % melview_endpoint, headers=headers, data=json.dumps(payload))
    return r.headers.get('Set-cookie')

def mitsu_getunits():
    r = requests.post("%s/api/rooms.aspx?_=1513470690197" % melview_endpoint, headers=headers)
    json_format = json.loads(r.text)
    return json_format[0]

def mitsu_sendcmd(unit_id, shortcmd, value):
    payload = {"unitid":"%s" % (unit_id), "v":2, "lc":1, "commands":"%s%s" %(shortcmd, value)}
    r = requests.post("%s/api/unitcommand.aspx" % melview_endpoint, headers=headers, data=json.dumps(payload))
    json_format = json.loads(r.text)
    return json_format
    
def mitsu_getstates():
    unit_state = []
    for unit_num in range(0, unit_count, 1):
        unit_id = int(unit_data["units"][unit_num]["unitid"])
        payload = {'unitid': unit_id, 'v': '2'}
        r = requests.post("%s/api/unitcommand.aspx" % melview_endpoint, headers=headers, data=json.dumps(payload))
        json_return = r.text
        unit_state.append(json.loads(json_return))
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
                
# Define event callbacks
def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc))
# Handle incoming MQQT message and translate
def on_message(client, obj, msg):
    # print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    # Break out the command and topic from the MQQT topic
    topic = msg.topic.split("/")
    unit_name= topic[2]
    command = topic[3][1:]
    data = msg.payload.decode('ascii')
    # Assign default to value, might be overriden later by specific commands
    value = data
    #print(unit_name + command + data)
    # Find Unit ID
    if command in mitsu_command_codes:
        for unit_num in range(0, unit_count, 1):
            if  unit_name.capitalize() in unit_data["units"][unit_num].values():
                unit_id = unit_data["units"][unit_num]["unitid"]      
        if command == 'setmode':
            if data == "off":
                value = 0
                command = 'power'
            else:
                value = aircon_modes.index(data)
        if command == 'setfan':
            value = aircon_cfanspeed[data]
        if command == 'airdir':
            value = aircon_cairdir[value]   
        r = mitsu_sendcmd(unit_id, mitsu_command_codes[command], value)
        # Send return data to MQTT and update Home Assistant
        mitsu_senddata(r)
        
    else:
        print("Unsupported command")
        return
#   if command == 'mode_command_topic':
#        mode = aircon_modes.index(msg.payload.decode('ascii'))
#        mqttc.publish('/sensors_hvac/%s/mode_state_topic' % unit_name, aircon_modes[unit_state[unit_num]["setmode"]])

#def on_publish(client, obj, mid):
#    print("mid: " + str(mid))
def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))
def on_log(client, obj, level, string):
    print(string)

def run_poller():
    #def run_poller():     
    mqttc.loop_forever()      
    mqttc.disconnect() 

if __name__ == '__main__':
    mqttc = mqtt.Client()
    # Assign event callbacks
    mqttc.on_message = on_message
    #mqttc.on_connect = on_connect
    #mqttc.on_publish = on_publish
    #mqttc.on_subscribe = on_subscribe
    
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
    mitsu_command_codes = {"setfan":"FS", "airdir":"AV", "setmode":"PW1,MD", "power":"PW", "settemp":"TS"}
    # Mapping values (Mitsubishi) to command words (HA)
    aircon_modes = ['0','heat','dry','cool','4','5','6','fan_only','auto','off']
    aircon_fanspeeds = ['auto','low','low','medium','medium','high','high']
    aircon_airdir = ['off','off','off','off','off','off','off','on']
    # Mapping words (HA) to command values (Mitsubishi)
    aircon_cairdir = {"off":3,"on":7}
    aircon_cfanspeed = {"auto":"0","low":"1","medium":"4","high":"6"}
    
        ## First we need to query the server and get a list of supported commands, 
    ## This will tell us what topics to subscribe to
    ## We do this once when the script is started
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
    # Uncomment to enable debug messages.
    #mqttc.on_log = on_log
    url = urlparse(mqqt_url_str)
    mqttc.username_pw_set(url.username, url.password)
    mqttc.connect(url.hostname, url.port)
    
    # Subscript to the HVAC topics
    for unit_num in range(0, unit_count, 1):
        unit_name = unit_data["units"][unit_num]["room"].lower()
        for key, value in unit_state[unit_num].items():
            topic = 'c'+key
            mqttc.subscribe([("/sensors_hvac/%s/%s" % (unit_name, topic), 0),("/sensors_hvac/downstairs/mode_command_topic", 0),("/sensors_hvac/lounge/target_temp", 0),("/sensors_hvac/downstairs/target_temp", 0)])
  
    
    
    createDaemon()




   