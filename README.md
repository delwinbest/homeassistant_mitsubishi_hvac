# Homeassistant Mitsubishi HVAC
This is a MQTT poller for the Mitsubishi range of WIFI controllers. Tested using the MAC-559IF-E Adapter.


## Requirements:
```
sudo apt-get install python3-pip
sudo pip3 install paho-mqtt configparser requests
```
To use the scripts, clone this repo into a direcory. Create the config file (see below), set up Home Assistant (also outlined below) and execute the script.

## Usage:
There are two scripts. 
mitsu_poller.py: Polls the Mitsubishi Melview API each time it is run. It publishes all unit data to MQTT
mitsu_command_poller.py: Daemonizes itself and subscripts to all MQTT topics for all units found. When a command is published to MQTT from
Home Assistant, this service relays it to the Melview API before updating the Home Assistant Queues.

To use, add a CRON which executes the script regularly, ie:
```
# m h  dom mon dow   command
*/5 * * * * /root/mitsu/mitsu_poller.py
```
NOTE: I would not poll more frequently than every 5 minutes. Melview have blocked my IP a couple of times during development probably assuming I'm DOS'ing their service.

## Configuration
In order to use the scripts, credentials are needed for the melview service as well as the MQQT broker.
Within the directory where the scripts are located, create a file named config.ini. This should contain creds in the following format:

```
[creds]
user: MELVIEW_USERNAME
password: MELVIEW_PASSWORD
endpoint: https://api.melview.net
mqqt_url_str: mqtt://MQQT_USER:MQQT_PASSWORD@m13.cloudmqtt.com:19089
```


## Home Assistant Sample Configuration
climate:
  - platform: mqtt
    name: Downstairs
    current_temperature_topic: /sensors_hvac/downstairs/current_temp
    temperature_command_topic: /sensors_hvac/downstairs/target_temp
    temperature_state_topic: /sensors_hvac/downstairs/temperature_state_topic
    power_command_topic: /sensors_hvac/downstairs/power_command_topic
    mode_command_topic: /sensors_hvac/downstairs/mode_command_topic
    mode_state_topic: /sensors_hvac/downstairs/mode_state_topic
  - platform: mqtt
    name: downstairs
    current_temperature_topic: /sensors_hvac/downstairs/current_temp
    temperature_command_topic: /sensors_hvac/downstairs/target_temp
    temperature_state_topic: /sensors_hvac/downstairs/temperature_state_topic
    power_command_topic: /sensors_hvac/downstairs/power_command_topic
    mode_command_topic: /sensors_hvac/downstairs/mode_command_topic
    mode_state_topic: /sensors_hvac/downstairs/mode_state_topic
    
     
## Mitsubishi Melview API return format
POST /api/unitcommand.aspx
{	"unitid":"116903",
	"v":2,
	"lc":1,
	"commands":"AV5"
}
REPLY:
{	"id":"116903",
	"lc":"",
	"power":1,
	"standby":0,
	"setmode":8,
	"automode":3,
	"setfan":0,
	"settemp":"23",
	"roomtemp":"24",
	"outdoortemp":"30",
	"airdir":5,
	"airdirh":3,
	"sendcount":0,
	"fault":"",
	"error":"ok"
}


List Units:
{'bschedule': '0',
 'building': 'Building',
 'buildingid': '9577',
 'units': [{'mode': '8',
            'power': 'on',
            'room': 'Lounge',
            'schedule1': 15003,
            'settemp': '23',
            'status': '',
            'temp': '23',
            'unitid': '114028',
            'wifi': '3'},
           {'mode': '8',
            'power': 'on',
            'room': 'Downstairs',
            'schedule1': 15002,
            'settemp': '23',
            'status': '',
            'temp': '23',
            'unitid': '116903',
            'wifi': '3'}]}


