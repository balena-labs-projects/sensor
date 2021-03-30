import os

def device_transform(device_name, fields):

    if device_name == "bme680":
        print("Transforming {0} value(s)...".format(device_name))
        for field in fields:
            if field == "humidityrelative":
                fields["humidity"] = fields.pop("humidityrelative")
            elif field == "temp":
                x = fields[field]
                if os.getenv('TEMP_UNIT', 'C') == 'F':
                    fields[field]= ((x/1000) * 1.8) + 32
                else:
                    fields[field] = x/1000
                fields["temperature"] = fields.pop("temp")

    elif device_name == "bme280":
        print("Transforming {0} value(s)...".format(device_name))
        for field in fields:
            if field == "humidityrelative":
                x = fields[field]
                fields[field] = x/1000 
                fields["humidity"] = fields.pop("humidityrelative")
            elif field == "temp":
                x = fields[field]
                if os.getenv('TEMP_UNIT', 'C') == 'F':
                    fields[field]= ((x/1000) * 1.8) + 32
                else:
                    fields[field] = x/1000 
                fields["temperature"] = fields.pop("temp")
            elif field == "pressure":
                x = fields[field]
                fields[field] = x * 10

    elif device_name == "bmp280":
        print("Transforming {0} value(s)...".format(device_name))
        for field in fields:
            if field == "temp":
                x = fields[field]
                if os.getenv('TEMP_UNIT', 'C') == 'F':
                    fields[field]= ((x/1000) * 1.8) + 32
                else:
                    fields[field] = x/1000 
                fields["temperature"] = fields.pop("temp")
            elif field == "pressure":
                x = fields[field]
                fields[field] = x * 10

    elif device_name == "htu21":
        print("Transforming {0} value(s)...".format(device_name))
        for field in fields:
            if field == "temp":
                x = fields[field]
                if os.getenv('TEMP_UNIT', 'C') == 'F':
                    fields[field]= ((x/1000) * 1.8) + 32
                else:
                    fields[field] = x/1000 
                fields["temperature"] = fields.pop("temp")
            if field == "humidityrelative":
                x = fields[field]
                fields[field] = x/1000 
                fields["humidity"] = fields.pop("humidityrelative")

    return fields
