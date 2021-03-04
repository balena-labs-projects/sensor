# sensor-block
Auto-detects connected i2c sensors and publsihes data on HTTP or MQTT.

## Usage
NOTE: This is still a POC. Start the server by going to /usr/src/app/scripts and run:

`python3 sensor.py`

You can poll the sensor data by doing `curl sensor:7575` from another container in the application.

## Features
- Uses Indusrial IO (iio) to communicate with sensors, utilizing drivers already in the kernel to talk to the sensor directly
- Data published via mqtt and/or http
- Provides raw sensor values or values compatible with balenaSense 2

## Overview/Compatibility
The following table lists sensors that are included in balenaOS that should work with this sensor block:

| Sensor Model | Sensor Name | Driver Name | Address(es) | Tested? |
| ------------ | ----------- | ----------- | ----------- | ------- |
| AD5301 | Analog Devices AD5446 and similar single channel DACs driver, TI DACs | ads5446 | 0xC, 0xD, 0xE, 0xF | Not tested |
| APDS9960 | Avago APDS9960 gesture/RGB/ALS/proximity sensor | apds9960 | 0x39 | Yes, NOT working |
| BME680 | Bosch Sensortec BME680 sensor | bme680 | 0x76, 0x77 | Yes, works |
| BMP180 | Bosch Sensortec BMP180 sensor | bmp280 | 0x77 | Not tested |
| BMP280 | Bosch Sensortec BMP280 sensor | bmp280 | 0x76, 0x77 | Yes, works |
| BME280 | Bosch Sensortec BME280 sensor | bmp280 | 0x76, 0x77 | Yes, works |
| HDC1000 | TI HDC100x relative humidity and temperature sensor | hdc100x | 0x40 - 0x43 | Not tested |
| HTU21 | Measurement Specialties HTU21 humidity & temperature sensor | htu21 | 0x40 | Yes, works |
| MS8607 | TE Connectivity PHT sensor | htu21 | 0x40, 0x76 | Not tested |
| MCP342x | Microchip Technology MCP3421/2/3/4/5/6/7/8 ADC | mcp3422 | 0x68 - 0x6F | Not tested |
| ADS1015 | Texas Instruments ADS1015 ADC | mcp3422 | 0x48 - 0x4B | Yes, NOT working |
| TSL4531 | TAOS TSL4531 ambient light sensors | tsl4531 | 0x29 | Not tested |
| VEML6070 | VEML6070 UV A light sensor | veml6070 | 0x38, 0x39 | Yes, works |

## Usage

**Docker compose file**

To use this image, create a container in your `docker-compose.yml` file as shown below:

```
services:
  sensor:
    build: .
    privileged: true
    cap_add:
      - ALL
    labels:
      io.balena.features.kernel-modules: '1'
      io.balena.features.sysfs: '1'
      io.balena.features.balena-api: '1'
```

## Data

The sensor data is available as json either as an mqtt payload or via the built-in webserver. To use mqtt, either include a container in your application that is named mqtt or provide an address for the MQTT_ADDRESS service variable (see below.)

If no mqtt container is present and no mqtt address is set, the webserver will be available on port 7575. To force the webserver to be active, set the ALWAYS_USE_WEBSERVER service variable to True.

The JSON for raw sensor data will be in the following format: 
```
{"humidityrelative": 0, "pressure": "738.220000000", "resistance": 0, "temp": "33480"}
```
If the `USE_BALENASENSE` service variable is set to `1`, the data will be in a format compatible with balenaSense:
```
[{'measurement': 'htu21', 'fields': {'humidityrelative': '29700', 'temp': '23356'}}, {'measurement': 'bmp280', 'fields': {'pressure': '99.911941406', 'temp': '23710'}}]
```
