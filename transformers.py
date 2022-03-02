import os

def device_transform(device_name, fields):

    # Create a dict copy to work on...
    # So we're not iterating a changing dict
    new_fields = fields.copy()

    if device_name == "bme680":
        print("Transforming {0} value(s)...".format(device_name))
        for field in fields:
            if field == "humidityrelative":
                new_fields["humidity"] = new_fields.pop("humidityrelative")
            elif field == "temp":
                x = fields[field]
                if os.getenv('TEMP_UNIT', 'C') == 'F':
                    new_fields[field]= ((x/1000) * 1.8) + 32
                else:
                    new_fields[field] = x/1000
                new_fields["temperature"] = new_fields.pop("temp")

    elif device_name == "bme280":
        print("Transforming {0} value(s)...".format(device_name))
        for field in fields:
            if field == "humidityrelative":
                new_fields[field] = fields[field]/1000
                new_fields["humidity"] = new_fields.pop("humidityrelative")
            elif field == "temp":
                x = fields[field]
                if os.getenv('TEMP_UNIT', 'C') == 'F':
                    new_fields[field]= ((x/1000) * 1.8) + 32
                else:
                    new_fields[field] = x/1000 
                new_fields["temperature"] = new_fields.pop("temp")
            elif field == "pressure":
                x = fields[field]
                new_fields[field] = x * 10

    elif device_name == "bmp280":
        print("Transforming {0} value(s)...".format(device_name))
        for field in fields:
            if field == "temp":
                x = fields[field]
                if os.getenv('TEMP_UNIT', 'C') == 'F':
                    new_fields[field] = ((x/1000) * 1.8) + 32
                else:
                    new_fields[field] = x/1000
                new_fields["temperature"] = new_fields.pop("temp")
            elif field == "pressure":
                x = fields[field]
                new_fields[field] = x * 10

    elif device_name == "htu21":
        print("Transforming {0} value(s)...".format(device_name))
        for field in fields:
            if field == "temp":
                x = fields[field]
                if os.getenv('TEMP_UNIT', 'C') == 'F':
                    new_fields[field]= ((x/1000) * 1.8) + 32
                else:
                    new_fields[field] = x/1000
                new_fields["temperature"] = new_fields.pop("temp")
            if field == "humidityrelative":
                x = fields[field]
                new_fields[field] = x/1000
                new_fields["humidity"] = new_fields.pop("humidityrelative")

    elif device_name == "sgp30":
        print("Transforming {0} value(s)...".format(device_name))
        for field in fields:
            if field == "concentration_co2":
                x = fields[field]
                new_fields[field] = x*1000000
            elif field == "concentration_voc":
                x = fields[field]
                new_fields[field] = x*1000000000
            elif ((field == "concentration_ethanol") or (field == "concentration_h2")):
                # both values not correct as driver does not calibrate them, so remove them
                new_fields.pop(field)

    return new_fields
