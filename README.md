# Homeassistant Mitsubishi HVAC
This is a MQTT poller for the Mitsubishi range of WIFI controllers. Tested using the MAC-559IF-E Adapter.


## Requirements:
```
sudo apt-get install python3-pip
sudo pip3 install paho-mqtt configparser requests
```

## Usage:
There are two scripts. 
mitsu_poller.py: Polls the Mitsubishi Melview API each time it is run. It publishes all unit data to MQTT
mitsu_command_poller.py: Daemonizes itself and subscripts to all MQTT topics for all units found. When a command is published to MQTT from
Home Assistant, this service relays it to the Melview API before updating the Home Assistant Queues.


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


