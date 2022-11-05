#!/usr/bin/env python3
import subprocess
import sys
from smbus2 import SMBus
import errno
import os
import iio
import json

from transformers import device_transform

class Reading:
    """Class for retrieving readings from devices."""

    def __init__(self, context: iio.Context):
        """
        Class constructor.
        Args:
            context: type=iio.Context
                Context used for retrieving the information.
        """
        self.context = context

    def write_reading(self):
        """Write the readings for the current context."""

        sensor_id = os.getenv('SENSOR_ID', '')
        UUID = os.environ.get('RESIN_DEVICE_UUID')[:7] # First seven chars of device UUID
        
        if os.getenv('COLLAPSE_FIELDS', 0) == "1":  # return just a dict of fields
            reading = {}
            for dev in self.context.devices:
                device_fields = self._device_read(dev)
                if os.getenv('RAW_VALUES', '1') == "1":
                    new_fields = device_fields
                else:
                    # send the device name and fields to the transform function
                    new_fields = device_transform(dev.name, device_fields)
                    
                # If sensor ID defined, add to fields:
                if sensor_id != '':
                    reading.update({"sensor_id": sensor_id})
                    
                # Add short UUID as field
                reading.update({"short_uuid": UUID})   
                          
                reading.update(new_fields)  # merges dicts, but overwrites equal values    

        else:   # return measurements and fields in a list
            reading = []
            for dev in self.context.devices:
                device_fields = self._device_read(dev)
                if os.getenv('RAW_VALUES', '1') == "1":
                    new_fields = device_fields
                else:
                    # send the device name and fields to the transform function
                    new_fields = device_transform(dev.name, device_fields)
                reading2 = {"measurement": dev.name, "fields": new_fields}
                reading.append(reading2)
                
                # If sensor ID defined, add to fields:
                if sensor_id != '':
                    reading3 = {"measurement": "sensor_ID", "fields": {"sensor_id": sensor_id}}
                    reading.append(reading3)
                    
                # Add short UUID to fields:
                reading3 = {"measurement": "short_UUID", "fields": {"short_uuid": UUID}}
                reading.append(reading3)

        return reading

    def _device_read(self, dev: iio.Device):
        reads = {}

        for channel in dev.channels:
            if not channel.output:
                chan = channel.id
                if len(channel.attrs) > 0:
                    for channel_attr in channel.attrs:
                        if channel_attr == "input" or channel_attr == "raw":
                            attr_value = self._channel_attribute_value(channel, channel_attr)
                            try:
                                reads[chan] = float(attr_value)
                            except:
                                reads[chan] = attr_value
            
        return reads

    @staticmethod
    def _channel_attribute_value(channel: iio.Channel, channel_attr: str):
        v = 0
        try:
            v = channel.attrs[channel_attr].value
        except OSError as err:
            print("Unable to read channel attribute " + channel_attr + ": " + err.strerror)

        return v

class IIO_READER:
    
    def __init__(self):
        print("Initializing IIO reader...")

    def get_readings(self, context):
        reading = Reading(context)
        x = reading.write_reading()
        return x
