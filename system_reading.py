#!/usr/bin/env python3
import os
import re
import subprocess
import sys

from transformers import device_transform


class WifiReader:
    """Reads and measures WiFi interfaces using the iwconfig utility"""

    def _run_cmd(self):
        """Runs the iwconfig command and returns its output"""
        try:
            return subprocess.check_output('iwconfig', stderr=subprocess.STDOUT, encoding='utf-8')
        except subprocess.CheckedProcessError as e:
            print("iwconfig cmd failed: {}".format(e.stderr))
            return ""

    def _read_output(self, output):
        """Finds WiFi interfaces in the iwconfig output.
        
        Returns a dictionary of the interfaces, where each interface has its own
        dictionary of statistics, like this:
           {<if_name>: {'quality_value':..., 'quality_max':..., 'signal_level':...}}
        """
        # Example iwconfig output
        # wlp0s20f3  IEEE 802.11  ESSID:"gal47lows"  
        #           Mode:Managed  Frequency:2.437 GHz  Access Point: C0:4A:00:9A:71:9D   
        #           Bit Rate:78 Mb/s   Tx-Power=22 dBm   
        #           Retry short limit:7   RTS thr:off   Fragment thr:off
        #           Power Management:on
        #           Link Quality=70/70  Signal level=-34 dBm  
        #           Rx invalid nwid:0  Rx invalid crypt:0  Rx invalid frag:0
        #           Tx excessive retries:22  Invalid misc:556   Missed beacon:0
        #
        # docker0   no wireless extensions.
        
        if_re = re.compile('^(?P<name>[\w:]+) +(IEEE +)?802.11')
        # Used to determine if we want to skip an interface
        mode_re = re.compile(' +Mode:(?P<mode>[\w-]+)')
        # Quality or Signal level may be invalid and so absent.
        link_re = re.compile(' +Link +(?P<quality>Quality[=:][\d/]+)? +(?P<signal>Signal level[=:][-\d\.]+)?')
        # Quality may be a single value or that value followed by max value and separated by '/'.
        quality_re = 'Quality[=:](?P<quality_value>\d+)/?(?P<quality_max>\d+)?'
        signal_re = 'Signal level[=:](?P<signal_level>[-\d\.]+)'
        result = {}

        lines = output.split('\n')
        # Iterate by line index so we can continue to parse lines for a particular
        # interface within an inner loop.
        for i in range(len(lines)):
            # find the next interface
            #print("Searching {}".format(lines[i]))
            m = re.search(if_re, lines[i])
            if m:
                if_dict = {}
                result[m.group('name')] = if_dict
                #print("Found I/F {}".format(m.group('name')))
                i += 1

                # Find link statistics for the interface. However, skip the
                # interface if it is an access point (mode = Master).
                is_master_mode = False
                for i in range(i, len(lines)):
                    m_mode = re.search(mode_re, lines[i])
                    if m_mode and m_mode.group('mode') == 'Master':
                        del result[m.group('name')]
                        break

                    m_link = re.search(link_re, lines[i])
                    if m_link:
                        if m_link.group('quality'):
                            m_quality = re.search(quality_re, lines[i])
                            if m_quality:
                                if_dict['quality_value'] = m_quality.group('quality_value')
                                # test for quality_max; expect None if not found
                                if m_quality.group('quality_max'):
                                    if_dict['quality_max'] = m_quality.group('quality_max')
                        if m_link.group('signal'):
                            m_signal = re.search(signal_re, lines[i])
                            if m_signal:
                                if_dict['signal_level'] = m_signal.group('signal_level')
                        # only 1 link line, so break to outer loop
                        break
                    else:
                        # If never found link line and starting a new interface,
                        # break to outer loop.
                        if re.search(if_re, lines[i]):
                            i -= 1
                            break
                    i += 1
            i += 1
        return result

    def read(self):
        output = self._run_cmd()
        self.result = {}
        if output:
            self.result = self._read_output(output)
        return self.result


class Reading:
    """
    Class for retrieving signal strength and link quality readings from WiFi interfaces.
    """

    def __init__(self, context):
        """context: type=SYSTEM_READER"""
        self._reader = context

    def write_reading(self):
        """Write the readings for the current context."""

        UUID = os.getenv('RESIN_DEVICE_UUID', '1234567')[:7] # First seven chars of device UUID
        self._reader.read()

        if os.getenv('COLLAPSE_FIELDS', 0) == "1":
            # return just a single dict of fields
            reading = {"short_uuid": UUID}
            for (name, device_fields) in self._reader.result.items():
                if os.getenv('RAW_VALUES', '1') == "1":
                    new_fields = device_fields
                else:
                    # send the device name and fields to the transform function
                    new_fields = device_transform(name, device_fields)
                # merges dicts, overwriting equal values
                reading.update(new_fields)

        else:
            # return measurements and fields in a list of dicts
            reading = [{"measurement": "short_UUID", "fields": {"short_uuid": UUID}}]
            for (name, device_fields) in self._reader.result.items():
                if os.getenv('RAW_VALUES', '1') == "1":
                    new_fields = device_fields
                else:
                    # send the device name and fields to the transform function
                    new_fields = device_transform(name, device_fields)
                reading2 = {"measurement": name, "fields": new_fields}
                reading.append(reading2)

        return reading


class SYSTEM_READER:
    """Reads WiFi interfaces"""

    def __init__(self):
        print("Initializing system reader")

    def device_count(self):
        wifi_raw = WifiReader().read()
        print("Found {} WiFi interfaces".format(len(wifi_raw)))
        return len(wifi_raw)

    def get_readings(self):
        return Reading(WifiReader()).write_reading()
