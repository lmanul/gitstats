"Does the work of looking for commits in repositories"

import datetime
import os
import re
import shlex
import subprocess

from util import date_to_key, get_git_branches

INS_DEL_PATTERN = re.compile(r".*changed, (\d+) insertion?.*, (\d+) deletion.*")
INS_PATTERN = re.compile(r".*changed, (\d+) insertion?.*")
DEL_PATTERN = re.compile(r".*changed, (\d+) deletion.*")

# Print some colors without having to depend on a module
GREEN_FG =  '\033[32m'
CYAN_FG = '\033[36m'
RESET = '\033[m' # reset to the defaults

def close_current_commit(days, all_messages, day, insertions, deletions, message,
        ignore_this_commit):
    if ignore_this_commit:
        return 0
    all_messages.append(message)
    if day is not None:
        if day not in days:
            days[day] = [0, 0, 0]
        days[day][0] += 1
        days[day][1] += insertions
        days[day][2] += deletions
        return 1
    return 0

def dig(accumulator, author, repo, branch):
    total_commits = 0
    all_messages = []
    print("" + GREEN_FG + ""
          "Looking for commits by '" + author + "' "
          "in " + repo + ":" + branch + ""
          "" + RESET)
    orig_dir = os.getcwd()
    if not os.path.exists(repo):
        print("Sorry, '" + repo + "' doesn't seem to exist. Skipping.")
        return
    os.chdir(repo)
    branches = get_git_branches()
    if branch not in branches:
        print("'" + branch + "' doesn't seem to exist. Skipping.")
        return
    os.system("git checkout " + branch)
    raw = subprocess.check_output(shlex.split("git log --author=" + author + " "
                                              "--stat")).decode("utf8")
    day = None
    insertions = 0
    deletions = 0
    commit_message = ""
    ignore_this_commit = False
    for line in raw.split("\n"):
        # Only keep one line of commit message for each commit
        if line.startswith("    ") and line.strip() != "" and commit_message == "":
            commit_message = line[4:]

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
                insertions = int(matches.group(1))
                deletions = int(matches.group(2))
            else:
                matches = INS_PATTERN.match(line)
                if matches:
                    insertions = int(matches.group(1))
                    deletions = 0
                else:
                    matches = DEL_PATTERN.match(line)
                    deletions = int(matches.group(1))
                    insertions = 0

        if line.startswith("commit"):
            if ignore_this_commit:
                ignore_this_commit = False
                continue
            total_commits += close_current_commit(
                accumulator, all_messages, day, insertions, deletions,
                commit_message, ignore_this_commit)
            commit_message = ""
    total_commits += close_current_commit(accumulator, all_messages, day,
        insertions, deletions, commit_message, ignore_this_commit)
    print(CYAN_FG + "Found " + str(total_commits) + " commits." + RESET)
    if total_commits > 0:
        print("\n\t* ".join(all_messages))
    os.chdir(orig_dir)
