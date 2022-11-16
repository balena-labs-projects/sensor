# sensor-block
Auto-detects connected i2c sensors and publsihes data on HTTP or MQTT.

## Features
- Uses Indusrial IO (iio) to communicate with sensors, utilizing drivers already in the kernel to talk to the sensor directly
- Data published via mqtt and/or http
- Provides raw sensor data or "tranforms" the sensor data into a more standardized format 
- json output can either be one measurement per sensor or all sensor fields in one list 

## Usage

**Docker compose file**

To use this image, create a container in your `docker-compose.yml` file as shown below:

```
services:
  sensor:
    image: bh.cr/balenalabs/sensor-<arch>
    privileged: true
    labels:
      io.balena.features.kernel-modules: '1'
      io.balena.features.sysfs: '1'
      io.balena.features.supervisor-api: '1'
    expose:
      - '7575'  # Only needed if using  http server
```

## Overview/Compatibility
This block utilizes the [Linux Industrial I/O Subsystem](https://wiki.analog.com/software/linux/docs/iio/iio) ("iio") which is a kernel subsystem that allows for ease of implementing drivers for sensors and other similar devices such as ADCs, DACs, etc.  You can see a list of available iio drivers [here](https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/tree/drivers/iio?h=linux-5.4.y) but in order to save space, most OSes do not include all these drivers. The easiest way to check if your board supports a driver is to use the modinfo command on a running device. For instance:
```
modinfo ti-ads1015
```
This command searches the running kernel for all the drivers it includes and prints out a description of any that are found to match. (Use the info in the Kconfig file in each folder of the driver list above to find the proper driver name to use with this command) BalenaOS for Raspberry Pi 3 includes a small subset of these drivers which are listed in the table below. As we continue to test sensors and improve the block, more sensors should be supported and the chart will be updated accordingly. Also note that as kernel and OS versions change, the supported drivers may change somewhat as well. It's best therefore to use modinfo as described above to test compatibility with any sensor being considered for use with this block.

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
| MS8607 | TE Connectivity PHT sensor | htu21 | 0x40, 0x76 | Yes, works partially (no pressure reading) |
| MCP342x | Microchip Technology MCP3421/2/3/4/5/6/7/8 ADC | mcp3422 | 0x68 - 0x6F | Not tested |
| ADS1015 | Texas Instruments ADS1015 ADC | ti-ads1015 | 0x48 - 0x4B | Yes, NOT working |
| TSL4531 | TAOS TSL4531 ambient light sensors | tsl4531 | 0x29 | Not tested |
| VEML6070 | VEML6070 UV A light sensor | veml6070 | 0x38, 0x39 | Yes, works |

By default, the block searches for sensors on SMBus number 1 (/dev/i2c-1) however you can set the bus number (an integer value) using the `BUS_NUMBER` service variable.

### Publishing Data

The sensor data is available in json format either as an mqtt payload and/or via the built-in http server. If you include an mqtt broker container named "mqtt" in your application, the block will automatically publish to that. If you provide an address for the `MQTT_ADDRESS` service variable, it will publish to that broker instead. The default interval for publishing data is eight seconds, which you can override with the `MQTT_PUB_INTERVAL` service variable by providing a value in seconds. The default topic is set to `sensors` (which is compatible with the [connector block](https://github.com/balena-labs-projects/connector#mqtt) ) which can be overridden by setting the `MQTT_PUB_TOPIC` service variable.

If no mqtt broker is set, the http server will be available on port 7575. To force the http server to be active even with mqtt, set the `ALWAYS_USE_HTTPSERVER` service variable to True.

The http data defaults to only be available to other containers in the application via `sensor:7575` - if you want this to be available externally, you'll need to map port 7575 to an external port in your docker-compose file.

## Data

The JSON for raw sensor data is available in one of two formats and is determined by the `COLLAPSE_FIELDS` service variable. The default value of `0` (zero) causes each sensor to output a separate measurement:
```
[{"measurement": "htu21", "fields": {"humidityrelative": 29700, "temp": 23356}}, {"measurement": "bmp280", "fields": {"pressure": 99.911941406, "temp": 23710}}, {"measurement": "short_UUID", "fields": {"short_uuid": "0f33e61"}}]
```

Changing `COLLAPSE_FIELDS` to `1` collapses all of the field values into one list like this:
```
{"short_uuid": "0f33e61", "humidityrelative": 29700, "temp": 23356, "pressure": 99.911941406}
```
Note that if two sensors output the same field name, it will only show up once in the list from one of the sensors. This feature is best used when the field names from sensors do not overlap.

The above examples display the raw data from the sensor as exposed by the driver, which is the default setting for the block. In many cases, the values and names need transformations to be useful. You can change the `RAW_VALUES` service variable from the default value of `1` to `0` (zero) to output transformed data instead. All the transformations are defined per-sensor in the `transformations.py` file which you can edit to your needs. We've included some basic ones for you. For example, here is the raw output of a bme680:
```
{"short_uuid": "0f33e61", "humidityrelative": 35.524, "pressure": 1005.48, "resistance": 52046.0, "temp": 24620.0}
```
Here is the transformed output with `RAW_VALUES` set to `0`:
```
{"short_uuid": "0f33e61", "pressure": 1005.4, "resistance": 65454.0, "humidity": 35.541, "temperature": 24.54}
```

When using transformed data outputs, you can change the temperature field from Celsius to Farenheit by setting the `TEMP_UNIT` variable to `F` (the default is `C`)

Note that the device's short UUID is always included in the data output, which can be useful for aggregating data from multiple devices. The short UUID is a string value so it will not show up in Grafana dashboards based on the [dashboard block](https://github.com/balena-labs-projects/dashboard).

## Use with other blocks

The sensor block works well with our [connector block](https://github.com/balena-labs-projects/connector) and [dashboard block](https://github.com/balena-labs-projects/dashboard). See the latest version of [balenaSense](https://github.com/balena-labs-projects/balena-sense) for an example of using all of these blocks together to read data from one or more sensor.
