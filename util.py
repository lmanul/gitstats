"Functions used in a few different modules"

import datetime
import shlex
import subprocess

def date_to_key(d):
    return "-".join([str(d.year), str(d.month).zfill(2), str(d.day).zfill(2)])

def date_from_key(k):
    parts = k.split("-")
    return datetime.datetime(int(parts[0]), int(parts[1]), int(parts[2]))

def quarter_string_from_date_string(s):
    (year, month, day) = s.split("-")
    quarter = str(1 + ((int(month) - 1) // 3))
    return year + "-Q" + str(quarter)

def get_git_branches():
    "Returns a list of git branch names in the current directory"
    raw = subprocess.check_output(shlex.split("git branch")).decode()
    branches = []
    for line in raw.split("\n"):
        line = line.strip()
        if line == "":
            continue
        if line.startswith("* "):
            line = line[2:]
        branches.append(line)
    return branches
