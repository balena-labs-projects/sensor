#!/usr/bin/env python3
import subprocess
import sys
from smbus2 import SMBus
import errno
import os
import iio
import json

from information import Information

class Reading:
    """Class for retrieving readings from devices."""

    def __init__(self, context):
        """
        Class constructor.
        Args:
            context: type=iio.Context
                Context used for retrieving the information.
        """
        self.context = context

    def write_reading(self):
        """Write the readings for the current context."""
        reading = []
        for dev in self.context.devices:
            reading2 = {"measurement": dev.name, "fields": self._device_read(dev)}
            reading.append(reading2)

        return reading

    def _device_read(self, dev):
        reads = {}

        for channel in dev.channels:
            if not channel.output:
                chan = channel.id
                if len(channel.attrs) > 0:
                    for channel_attr in channel.attrs:
                        if channel_attr == "input" or channel_attr == "raw":
                            reads[chan] = self._channel_attribute_value(channel, channel_attr)

        return reads

    @staticmethod
    def _channel_attribute_value(channel, channel_attr):
        v = 0
        try:
            v = channel.attrs[channel_attr].value
        except OSError as err:
            print("Unable to read channel attribute " + channel_attr + ": " + err.strerror)

        return v

class IIO_READER:
    data = None

    def __init__(self):
        print("initializing reading")

    def get_readings(self, context):
        information = Information(context)
        reading = Reading(context)
        x = reading.write_reading()
        return x
