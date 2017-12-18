# Homeassistant Mitsubishi HVAC
This is a MQTT poller for the Mitsubishi range of WIFI controllers. Tested using the MAC-559IF-E Adapter.


## Requirements:
pip3 install paho-mqtt

## Usage:
TBC, rough notes:

climate:
  - platform: mqtt
    name: Downstairs
    current_temperature_topic: /sensors/hvac_downstairs/current_temp
    temperature_command_topic: /sensors/hvac_downstairs/target_temp
    temperature_state_topic: /sensors/hvac_downstairs/temperature_state_topic
    power_command_topic: /sensors/hvac_downstairs/power_command_topic
    mode_command_topic: /sensors/hvac_downstairs/mode_command_topic
    mode_state_topic: /sensors/hvac_downstairs/mode_state_topic

