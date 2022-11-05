import os

def device_transform(device_name: str, fields: dict) -> dict:

    # Create a dict copy to work on...
    # So we're not iterating a changing dict
    new_fields = fields.copy()

    if device_name == "bme680":
        print("Transforming {0} value(s)...".format(device_name))
        for field in fields:
            if field == "humidityrelative":
                new_fields["humidity"] = new_fields.pop("humidityrelative")
            elif field == "temp":
                val = fields[field]
                if os.getenv('TEMP_UNIT', 'C') == 'F':
                    new_fields[field]= ((val/1000) * 1.8) + 32
                else:
                    new_fields[field] = val/1000
                new_fields["temperature"] = new_fields.pop("temp")

    elif device_name == "bme280":
        print("Transforming {0} value(s)...".format(device_name))
        for field in fields:
            if field == "humidityrelative":
                new_fields[field] = fields[field]/1000
                new_fields["humidity"] = new_fields.pop("humidityrelative")
            elif field == "temp":
                val = fields[field]
                if os.getenv('TEMP_UNIT', 'C') == 'F':
                    new_fields[field]= ((val/1000) * 1.8) + 32
                else:
                    new_fields[field] = val/1000 
                new_fields["temperature"] = new_fields.pop("temp")
            elif field == "pressure":
                val = fields[field]
                new_fields[field] = val * 10

    elif device_name == "bmp280":
        print("Transforming {0} value(s)...".format(device_name))
        for field in fields:
            if field == "temp":
                val = fields[field]
                if os.getenv('TEMP_UNIT', 'C') == 'F':
                    new_fields[field] = ((val/1000) * 1.8) + 32
                else:
                    new_fields[field] = val/1000
                new_fields["temperature"] = new_fields.pop("temp")
            elif field == "pressure":
                val = fields[field]
                new_fields[field] = val * 10

    elif device_name == "htu21" or device_name == "dht11":
        print("Transforming {0} value(s)...".format(device_name))
        for field in fields:
            if field == "temp":
                val = fields[field]
                if os.getenv('TEMP_UNIT', 'C') == 'F':
                    new_fields[field]= ((val/1000) * 1.8) + 32
                else:
                    new_fields[field] = val/1000
                new_fields["temperature"] = new_fields.pop("temp")
            if field == "humidityrelative":
                val = fields[field]
                new_fields[field] = val/1000
                new_fields["humidity"] = new_fields.pop("humidityrelative")

    return new_fields
