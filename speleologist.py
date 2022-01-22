"Does the work of looking for commits in repositories"

import datetime
import os
import re
import shlex
import subprocess

from util import date_to_key

INS_DEL_PATTERN = re.compile(r".*changed, (\d+) insertion?.*, (\d+) deletion.*")
INS_PATTERN = re.compile(r".*changed, (\d+) insertion?.*")
DEL_PATTERN = re.compile(r".*changed, (\d+) deletion.*")

def close_current_commit(days, day, insertions, deletions, ignore_this_commit):
    if ignore_this_commit:
        return
    if day is not None:
        if day not in days:
            days[day] = [0, 0, 0]
        days[day][0] += 1
        days[day][1] += insertions
        days[day][2] += deletions

def dig(accumulator, author, repo):
    print("Looking for commits by '" + author + "' in " + repo)
    orig_dir = os.getcwd()
    os.chdir(repo)
    os.system("git checkout master")
    raw = subprocess.check_output(shlex.split("git log --author=" + author + " "
                                              "--stat")).decode()
    day = None
    insertions = 0
    deletions = 0
    ignore_this_commit = False
    for line in raw.split("\n"):
        line = line.strip()
        if line.startswith("Date:"):
            date = datetime.datetime.strptime(line[8:],
                                              "%a %b %d %H:%M:%S %Y %z")
            day = date_to_key(date)
        if "static-sites" in line and "prod" in line and "live" in line:
            # This is an automated static-sites push
            ignore_this_commit = True
        if "changed" in line and ("insertion" in line or "deletion" in line):
            matches = INS_DEL_PATTERN.match(line)
            if matches:
                insertions = int(matches[1])
                deletions = int(matches[2])
            else:
                matches = INS_PATTERN.match(line)
                if matches:
                    insertions = int(matches[1])
                    deletions = 0
                else:
                    matches = DEL_PATTERN.match(line)
                    deletions = int(matches[1])
                    insertions = 0

        if line.startswith("commit"):
            if ignore_this_commit:
                ignore_this_commit = False
                continue
            close_current_commit(accumulator, day, insertions, deletions,
                                 ignore_this_commit)
    close_current_commit(accumulator, day, insertions, deletions,
                         ignore_this_commit)
    os.chdir(orig_dir)
