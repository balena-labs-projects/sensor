#!/usr/bin/env python3
import subprocess
import sys
from smbus2 import SMBus
import errno
import os
import iio
import json


def _create_context():


    return iio.Context()


class Information:
    """Class for retrieving the iio information."""

    def __init__(self, context):
        """
        Class constructor.
        Args:
            context: type=iio.Context
                Context used for retrieving the information.
        """
        self.context = context

    def print_information(self):
        """Print the information about the current context."""
        self._context_info()

    def _context_info(self):
        print("IIO context created: " + self.context.name)
        print("Backend version: %u.%u (git tag: %s)" % self.context.version)
        print("Backend description string: " + self.context.description)

        if len(self.context.attrs) > 0:
            print("IIO context has %u attributes: " % len(self.context.attrs))

        for attr, value in self.context.attrs.items():
            print("\t" + attr + ": " + value)

        print("IIO context has %u devices:" % len(self.context.devices))

        for dev in self.context.devices:
            self._device_info(dev)

    def _device_info(self, dev):
        print("\t" + dev.id + ": " + dev.name)

        if dev is iio.Trigger:
            print("Found trigger! Rate: %u HZ" % dev.frequency)

        print("\t\t%u channels found: " % len(dev.channels))
        for channel in dev.channels:
            self._channel_info(channel)

        if len(dev.attrs) > 0:
            print("\t\t%u device-specific attributes found: " % len(dev.attrs))
            for device_attr in dev.attrs:
                self._device_attribute_info(dev, device_attr)

        if len(dev.debug_attrs) > 0:
            print("\t\t%u debug attributes found: " % len(dev.debug_attrs))
            for debug_attr in dev.debug_attrs:
                self._device_debug_attribute_info(dev, debug_attr)

    def _channel_info(self, channel):
        print("\t\t\t%s: %s (%s)" % (channel.id, channel.name or "", "output" if channel.output else "input"))
        if len(channel.attrs) > 0:
            print("\t\t\t%u channel-specific attributes found: " % len(channel.attrs))
            for channel_attr in channel.attrs:
                self._channel_attribute_info(channel, channel_attr)

    @staticmethod
    def _channel_attribute_info(channel, channel_attr):
        try:
            print("\t\t\t\t" + channel_attr + ", value: " + channel.attrs[channel_attr].value)
        except OSError as err:
            print("Unable to read " + channel_attr + ": " + err.strerror)

    @staticmethod
    def _device_attribute_info(dev, device_attr):
        try:
            print("\t\t\t" + device_attr + ", value: " + dev.attrs[device_attr].value)
        except OSError as err:
            print("Unable to read " + device_attr + ": " + err.strerror)

    @staticmethod
    def _device_debug_attribute_info(dev, debug_attr):
        try:
            print("\t\t\t" + debug_attr + ", value: " + dev.debug_attrs[debug_attr].value)
        except OSError as err:
            print("Unable to read " + debug_attr + ": " + err.strerror)
