# Homeassistant Mitsubishi HVAC
This is a MQTT poller for the Mitsubishi range of WIFI controllers. Tested using the MAC-559IF-E Adapter.


## Requirements:
pip3 install paho-mqtt
pip3 install configparser

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
    name: Lounge
    current_temperature_topic: /sensors_hvac/lounge/current_temp
    temperature_command_topic: /sensors_hvac/lounge/target_temp
    temperature_state_topic: /sensors_hvac/lounge/temperature_state_topic
    power_command_topic: /sensors_hvac/lounge/power_command_topic
    mode_command_topic: /sensors_hvac/lounge/mode_command_topic
    mode_state_topic: /sensors_hvac/lounge/mode_state_topic