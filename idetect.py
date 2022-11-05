#!/usr/bin/env python3
import subprocess
import sys
from smbus2 import SMBus
import errno
import os
import iio
import time
import iio
from typing import Set, Dict

# Decimal address values
i2c_devices: Dict[int,str] = {
12:     "ad5446",
13:     "ad5446",
14:     "ad5446",
15:     "ad5446",
41:     "tsl4531",
56:     "veml6070",
57:     "multiple",
64:     "multiple",
65:     "hdc100x",
66:     "hdc100x",
67:     "hdc100x",
64:     "multiple",
72:     "ti-ads1015",
73:     "ti-ads1015",
74:     "ti-ads1015",
75:     "ti-ads1015",
104:    "mcp3422",
105:    "mcp3422",
106:    "mcp3422",
107:    "mcp3422",
108:    "mcp3422",
109:    "mcp3422",
110:    "mcp3422",
111:    "mcp3422",
118:    "multiple",
119:    "multiple"
}

# List of supported iio devices (superset of i2c devices)
iio_device_names: Set[str] = {
    "dht11", # Also applies to the DHT22
    *set(i2c_devices.values())
}

del_drivers = {
"ad5446.c": "ad5446.c",
"apds9960": "apds9960",
"bme680": "bme680-i2c",
"bmp280": "bmp280-i2c",
#"dht11": "dht11",
"hdc100": "hdc100",
"htu21": "htu21",
"mcp320x": "mcp320x",
"mcp3422": "mcp3422",
"ti-ads1015": "ti-ads1015",
"tsl4531": "tsl4531",
"veml6070": "veml6070"
}

bosch_chip_id = {
0x61: "bme680",
0x55: "bmp180",
0x58: "bmp280",
0x60: "bme280"
}

def read_chip_id(bus, device, loc):
    chip_id = -1
    try:
        chip_id = bus.read_byte_data(device, loc)
    except Exception as e:
            print("Error while reading chip ID of device at address {0}: {1}".format(e, hex(device)))
    
    if chip_id == -1:  # Wait a tiny bit and try one more time
        time.sleep(2)
        try:
            chip_id = bus.read_byte_data(device, loc)
        except Exception as e:
            print("Error again while reading chip ID of device at address {0}: {1}".format(e, hex(device)))

    return chip_id

def detect_i2c_sensors():
    bus_number = int(os.getenv('BUS_NUMBER', '1'))  # default 1 indicates /dev/i2c-1
    bus = SMBus(bus_number)
    device_count = 0
    active = []
    chip_id = 0

    print("======== Searching i2c bus for devices... ========")
    for device in range(3, 128):
        try:
            bus.write_byte(device, 0)
            print("Found device at {0}".format(hex(device)))
            active.append(device)
            device_count = device_count + 1
        except IOError as e:
            if e.errno != errno.EREMOTEIO:
                #print("Warning: {0} on address {1}".format(e, hex(device)))
                if e.errno == 16:  # device busy
                    print("Found (busy) device at {0}".format(hex(device)))
                    active.append(device)
                    device_count = device_count + 1
        except Exception as e: # exception if read_byte fails
            print("Error while searching for devices on i2c: {0} on address {1}".format(e, hex(device)))

    # use i2cdetect to see if HTU21D is on address 64 (0x40) since nothing else seems to detect it
    if 64 not in active:
        p = subprocess.Popen(['i2cdetect', '-y','1'],stdout=subprocess.PIPE,)
        for i in range(0,6):
            line = str(p.stdout.readline())
            #print(line)
            if line.find("40: 40") > 0:
                active.append(64)
                print("Found device (via i2cdetect) at 0x40")
    if device_count > 0:
        # We want to remove any existing devices if they are present
        # First uninstantiate the i2c bus
        print("======== Removing existing devices from the i2c bus... ========")
        for device in active:
            print("Deleting device found at {0}.".format(hex(device)))
            delete_device = "echo {0} > /sys/bus/i2c/devices/i2c-1/delete_device".format(hex(device))
            os_out = os.system(delete_device)
            if os_out > 0:
                print("Delete device {0} exit code: {1}".format(hex(device), os_out))

        print("======== Unloading any existing modules... ========")
        # Next unload any present devices using modprobe -rv
        output = subprocess.check_output("lsmod").decode()  # TODO: replace check_output with run variant
        active_modules = set()
        i = 0
        for line in output.split('\n'):
            i = i + 1
            if i > 1:
                line = line.strip()
                if line:
                    lsmod_module = line.split()   # splits string at whitespaces
                    find_underscore = lsmod_module[0].find("_")   # equals -1 if no underscore
                    if find_underscore > 0:
                        mod_name = lsmod_module[0][0:find_underscore]  # strip underscore and everything following
                    else:
                        mod_name = lsmod_module[0]
                    active_modules.add(mod_name)
        # find in dict
        #print("Currently loaded modules: {0}".format(dd))
        for x in active_modules:
            if x in del_drivers:
                print("Unloading module {0} as {1}.".format(x, del_drivers[x]))
                subprocess.run(["modprobe", "-r", x])

        # Remove unrecognized devices
        #print("Active: {0}".format(active))
        #print("Keys: {0}".format(devices.keys()))
        new_active = []
        for x in active:
            if x in i2c_devices.keys():
                new_active.append(x)
            else:
                print("Device at {0} not in known supported drivers.".format(hex(x)))

        print("New active: {0}".format(new_active))

        # Now, load all the devices found
        print("======== Loading devices found... ========")
        subprocess.run(["modprobe", "crc8"])
        subprocess.run(["modprobe", "industrialio"])
        new_active_count = 0
        for device in new_active:
            if i2c_devices[device] != "multiple":
                print("Loading device {0} on address {1}.".format(i2c_devices[device], hex(device)))
                subprocess.run(["modprobe", i2c_devices[device]])
                new_device = "echo {0} {1} > /sys/bus/i2c/devices/i2c-1/new_device".format(i2c_devices[device], hex(device))
                os_out = os.system(new_device)
                if os_out > 0:
                    print("New device {0} exit code: {1}".format(hex(device), os_out))
                new_active_count = new_active_count + 1
            else:
                load_device = ""
                mod_device = ""
                if device == 57:
                    if read_chip_id(bus, device, 146) == 0xAB:
                        mod_device = "apds9960"
                    else:
                        mod_device = "veml6070"

                elif device == 64:
                    #print("hello64")
                    chip_id = read_chip_id(bus, device, 255)
                    #print("chipid = {0}".format(chip_id))
                    if chip_id == 0x1000 or chip_id == 0x1050:
                        mod_device = "hdc100x"
                    else:
                        mod_device = "htu21"

                elif ((device == 118) and (64 not in new_active)) or (device == 119):
                   chip_id = read_chip_id(bus, device, 208)
                   if chip_id > 0:
                       load_device = bosch_chip_id[read_chip_id(bus, device, 208)]
                       if load_device == "bme680":
                           mod_device = "bme680-i2c"
                       else:
                           mod_device = "bmp280-i2c"

                if mod_device != "":
                    if load_device == "":
                        load_device = mod_device
                    subprocess.run(["modprobe", mod_device])
                    print("Loading device {0} (chip ID {1}) on address {2}.".format(mod_device, chip_id, hex(device)))
                    new_device = "echo {0} {1} > /sys/bus/i2c/devices/i2c-1/new_device".format(load_device, hex(device))
                    os_out = os.system(new_device)
                    if os_out > 0:
                        print("New device exit code: {0}".format(os_out))
                    new_active_count = new_active_count + 1

        print("Loaded {0} of {1} device(s) found".format(new_active_count, device_count))
        bus.close()
        bus = None
        return new_active_count

    else:  # no devices found
        bus.close()
        bus = None
        return 0
    
def detect_iio_sensors(
    strict: bool,
    context: iio.Context,
    supported_devices: Set[str] = iio_device_names
) -> int:
    """Fetches number of iio (supported) devices inside the iio context.

    Args:
        strict (bool): Return only the number of detected devices whose names are in supported_devices
        context (iio.Context): iio Context
        supported_devices(Set[str]): Names of supported devices

    Returns:
        int: Nr of (supported) iio devices detected.
    """

    nr_devices = 0

    if strict:
        for device in context.devices:
            if device.name in supported_devices:
                nr_devices += 1
    else:
        nr_devices = len(context.devices)
    
    return nr_devices

def detect_sensors(context: iio.Context) -> int:
    detection_mode = os.getenv("DETECT_SENSORS", "I2C")
    print("Sensor detection mode: {0}".format(detection_mode))

    if detection_mode == "I2C":
        return detect_i2c_sensors()
    elif detection_mode == "IIO_STRICT":
        return detect_iio_sensors(True, context)
    elif detection_mode == "IIO":
        return detect_iio_sensors(False, context)
    else:
        print("Unknown value for env variable DETECT_SENSORS: {0}".format(detection_mode))
        return 0
