import pandas as pd
import re


# https://gis.stackexchange.com/questions/398021/converting-degrees-decimal-minutes-to-decimal-degrees-in-python
def ddm2dec(dms_str):
    """Return decimal representation of degree decimal minutes"""
    if pd.isna(dms_str):
        return

    sign = -1 if re.search("[swSW]", dms_str) else 1

    matches = re.search(r"(\d+) (\d*).(\d*)", dms_str)
    if matches:
        numbers = matches.groups()
    else:
        matches = re.search(r"(\d+)° *(\d*).(\d*)\'", dms_str)
        numbers = matches.groups()

    degree = numbers[0]
    minute_decimal = numbers[1]
    decimal_val = numbers[2] if len(numbers) > 2 else "0"
    minute_decimal += "." + decimal_val

    return sign * (int(degree) + float(minute_decimal) / 60)
