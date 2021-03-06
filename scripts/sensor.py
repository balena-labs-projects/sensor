#!/usr/bin/env python3
import sys
import errno
import os
import iio
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

import idetect
from reading import IIO_READER

class balenaSense():
    readfrom = 'unset'

    def __init__(self):
        # First, use iio to detect supported sensors
        self.device_count = idetect.detect_iio_sensors()

        if self.device_count > 0:
            self.readfrom = "iio_sensors"
            self.context = _create_context()
            self.sensor = IIO_READER()

        # More sensor types can be added here
        # make sure to change the value of self.readfrom


        # If this is still unset, no sensors were found; quit!
        if self.readfrom == 'unset':
            print('No suitable sensors found! Exiting.')
            sys.exit()

    def sample(self):
        if self.readfrom == 'sense-hat':
            return self.apply_offsets(self.sense_hat_reading())
        elif self.readfrom == 'iio_sensors':
            return self.sensor.get_readings(self.context)
        else:
            return self.sensor.get_readings(self.sensor)


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
        self.wfile.write(json.dumps(measurements).encode('UTF-8'))

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
