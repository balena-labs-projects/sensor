# This script detects for the presence of either a BME680 sensor on the I2C bus or a Sense HAT
# The BME680 includes sensors for temperature, humidity, pressure and gas content
# The Sense HAT does not have a gas sensor, and so air quality is approximated using temperature and humidity only.

#!/usr/bin/env python3
import sys
import errno
import os
import iio
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

import idetect
from iio_reader import IIO_READER

class balenaSense():
    readfrom = 'unset'

    def __init__(self):
        # First, use iio to detect supported sensors
        self.device_count = idetect.detect_iio_sensors()

        if self.device_count > 0:
            self.readfrom = "iio_sensors"
            self.sensor = IIO_READER()

        # Next, check if there is a 1-wire temperature sensor (e.g. DS18B20)
        if self.readfrom == 'unset':
            if os.environ.get('BALENASENSE_1WIRE_SENSOR_ID') != None:
                sensor_id = os.environ['BALENASENSE_1WIRE_SENSOR_ID']
            else:
                sensor_id = None

            try:
                self.sensor = W1THERM(sensor_id)
            except:
                print('1-wire sensor not found')
            else:
                self.readfrom = '1-wire'
                print('Using 1-wire for readings (temperature only)')

        # If this is still unset, no sensors were found; quit!
        if self.readfrom == 'unset':
            print('No suitable sensors found! Exiting.')
            sys.exit()

    def sample(self):
        if self.readfrom == 'sense-hat':
            return self.apply_offsets(self.sense_hat_reading())
        else:
            return self.apply_offsets(self.sensor.get_readings(self.sensor))


    def apply_offsets(self, measurements):
        # Apply any offsets to the measurements before storing them in the database
        if os.environ.get('BALENASENSE_TEMP_OFFSET') != None:
            measurements[0]['fields']['temperature'] = measurements[0]['fields']['temperature'] + float(os.environ['BALENASENSE_TEMP_OFFSET'])

        if os.environ.get('BALENASENSE_HUM_OFFSET') != None:
            measurements[0]['fields']['humidity'] = measurements[0]['fields']['humidity'] + float(os.environ['BALENASENSE_HUM_OFFSET'])

        if os.environ.get('BALENASENSE_ALTITUDE') != None:
            # if there's an altitude set (in meters), then apply a barometric pressure offset
            altitude = float(os.environ['BALENASENSE_ALTITUDE'])
            measurements[0]['fields']['pressure'] = measurements[0]['fields']['pressure'] * (1-((0.0065 * altitude) / (measurements[0]['fields']['temperature'] + (0.0065 * altitude) + 273.15))) ** -5.257

        return measurements


def _create_context():

    return iio.Context()


class balenaSenseHTTP(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        measurements = balenasense.sample()
        self.wfile.write(json.dumps(measurements[0]['fields']).encode('UTF-8'))

    def do_HEAD(self):
        self._set_headers()


if __name__ == "__main__":

    # Start the server to answer requests for readings
    balenasense = balenaSense()

    while True:
        server_address = ('', 7575)
        httpd = HTTPServer(server_address, balenaSenseHTTP)
        print('Sensor HTTP server running')
        httpd.serve_forever()
