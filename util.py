"Functions used in a few different modules"

import datetime

def date_to_key(d):
    return "-".join([str(d.year), str(d.month).zfill(2), str(d.day).zfill(2)])

def date_from_key(k):
    parts = k.split("-")
    return datetime.datetime(int(parts[0]), int(parts[1]), int(parts[2]))

def quarter_string_from_date_string(s):
    (year, month, day) = s.split("-")
    quarter = str(1 + ((int(month) - 1) // 3))
    return year + "-Q" + str(quarter)
