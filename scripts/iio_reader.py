import subprocess
import json
import threading
import io
import time

from information import Information
from reading import Reading

class IIO_READER:
    data = None
    #context = None

    def __init__(self):
        print("initializing reading")
        #context = my_context

    def get_readings(self, context):
        information = Information(context)
        information.write_information()
        reading = Reading(context)
        x = reading.write_reading()
        return x
