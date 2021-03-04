# sensor-block
Auto-detects connected i2c sensors and publsihes data on HTTP or MQTT.

NOTE: This is still a POC. Start the server by going to /usr/src/app/scripts and run `python3 sensor.py`.

## Features
- Uses Indusrial IO (iio) to communicate with sensors - no drivers needed for supported sensors
- Main building block for balenaSense 2

## Overview/Compatibility
The following table lists sensors that are supported on the Raspberry Pi using balenaOS:
