#!/usr/bin/env python3
import sys
import errno
import os
import iio
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from balena import Balena
import paho.mqtt.client as mqtt
import socket
import threading

import idetect
from reading import IIO_READER
from information import Information

# Use the sdk to get services
def mqtt_detect():
    print("Using API to detect services...")
    balena = Balena()
    auth_token = os.environ.get('BALENA_API_KEY')
    balena.auth.login_with_token(auth_token)
    device_id = os.environ.get('BALENA_DEVICE_UUID')
    device = balena.models.device.get_with_service_details(device_id, False)
    for service in device['current_services']:
        if service == "mqtt":
            print("Found a service on this device named 'mqtt'")
            return True
    return False

class balenaSense():
    readfrom = 'unset'

    def __init__(self):
        print("Initializing sensors...")
        # First, use iio to detect supported sensors
        self.device_count = idetect.detect_iio_sensors()

        if self.device_count > 0:
            self.readfrom = "iio_sensors"
            self.context = _create_context()
            self.sensor = IIO_READER()
            # Print the iio info
            information = Information(self.context)
            information.write_information()

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

# Simple webserver
def background_web(server_socket):
    balenasense = balenaSense()
    while True:
        # Wait for client connections
        client_connection, client_address = server_socket.accept()

        # Get the client request
        request = client_connection.recv(1024).decode()
        print(request)

        # Send HTTP response
        response = 'HTTP/1.0 200 OK\n\n'+ json.dumps(balenasense.sample())
        client_connection.sendall(response.encode())
        client_connection.close()


if __name__ == "__main__":

    mqtt_address = os.getenv('MQTT_ADDRESS', 'none')
    enable_webserver = os.getenv('ALWAYS_USE_WEBSERVER', 0)

    if mqtt_detect() and mqtt_address == "none":
        mqtt_address = "mqtt"

    #TEST - REMOVE THESE LINES
    #mqtt_address = "192.168.1.65"
    #enable_webserver = "True"

    if mqtt_address != "none":
        print("Starting mqtt client, publishing to {0}:1883".format(mqtt_address))
        client = mqtt.Client()
        try:
            client.connect(mqtt_address, 1883, 60)
        except Exception as e:
            print("Error connecting to mqtt. ({0})".format(str(e)))
            mqtt_address = "none"
            enable_webserver = "True"
        else:
            client.loop_start()
            balenasense = balenaSense()
    else:
        enable_webserver = "True"

    if enable_webserver == "True":
        SERVER_HOST = '0.0.0.0'
        SERVER_PORT = 7575

        # Create socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen(1)
        print("Web server listening on port {0}...".format(SERVER_PORT))

        t = threading.Thread(target=background_web, args=(server_socket,))
        t.start()

    while True:
        if mqtt_address != "none":
            client.publish('sensor_data', json.dumps(balenasense.sample()))
        time.sleep(8)
