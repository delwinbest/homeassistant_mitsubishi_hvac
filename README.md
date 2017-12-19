# Homeassistant Mitsubishi HVAC
This is a MQTT poller for the Mitsubishi range of WIFI controllers. Tested using the MAC-559IF-E Adapter.


## Requirements:
pip3 install paho-mqtt
pip3 install configparser
pip3 install requests

## Usage:
TBC, rough notes:

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
    
    
    
    
## Melview API return format
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


