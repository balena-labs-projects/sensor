import subprocess
import json
import threading
import io
import time

class IIO_READER:
    data = None

    def __init__(self):
        print("initializing reading")

    def get_readings(self, sensor):
        return [
            {
                'measurement': 'balena-sense',
                'fields': {
                    'value-1': 101.1,
                    'value-2': 102.1,
                    'value-3': 104.5
                }
            }
        ]
