"Produces a graph showing some statistics in git repositories"

import argparse
import datetime
import sys

from grapher import draw_weeks_and_quarters
from speleologist import dig
from util import date_from_key
from util import date_to_key
from util import quarter_string_from_date_string

def flatten(l):
    "Flattens a nested list"
    flattened = []
    for sublist in l:
        for element in sublist:
            flattened.append(element)
    return flattened

def distill_to_weeks(days):
    "Gathers daily data into weekly"
    weeks = {}
    day_keys = sorted(list(days.keys()))

    # Get the first Monday before the first recorded commit.
    first_monday = date_from_key(day_keys[0])
    while first_monday.isoweekday() != 1:
        first_monday = first_monday - datetime.timedelta(days=1)

    last_monday = date_from_key(day_keys[len(day_keys) - 1])
    while last_monday.isoweekday() != 1:
        last_monday = last_monday - datetime.timedelta(days=1)

    current_monday = first_monday
    while current_monday <= last_monday:
        commit_count = 0
        ins_count = 0
        del_count = 0
        for i in range(0, 7):
            d = current_monday + datetime.timedelta(days=i)
            k = date_to_key(d)
            if k in days:
                commit_count += days[k][0]
                ins_count += days[k][1]
                del_count += days[k][2]
        weeks[date_to_key(current_monday)] = [commit_count, ins_count, del_count]
        current_monday = current_monday + datetime.timedelta(days=7)
    return weeks

def distill_to_quarters(days):
    "Gathers daily data into quarterly"
    quarters = {}
    day_keys = sorted(list(days.keys()))
    quarter_key = quarter_string_from_date_string(day_keys[0])
    commit_count = 0
    ins_count = 0
    del_count = 0
    for day_key in day_keys:
        new_quarter_key = quarter_string_from_date_string(day_key)
        if new_quarter_key != quarter_key:
            quarters[quarter_key] = [commit_count, ins_count, del_count]
            commit_count = 0
            ins_count = 0
            del_count = 0
            quarter_key = new_quarter_key
        commit_count += days[day_key][0]
        ins_count += days[day_key][1]
        del_count += days[day_key][2]
    # Close out the last remaining quarter
    quarters[quarter_key] = [commit_count, ins_count, del_count]
    return quarters

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--author", dest="author", action="append",
                        nargs="+", help="The author(s) to look for")
    parser.add_argument("-b", "--branch", dest="branch", action="store",
                        default="master", nargs="?",
                        help="The branch (default is 'master')")
    parser.add_argument("-r", "--repo", dest="repos", action="append",
                        nargs="+", help="The repository(ies) where to look")
    parser.add_argument("-o", "--output", dest="output", action="store",
                        nargs="?", help="The name of the output file",
                        default="stats.html")
    args = parser.parse_args()

    SHOULD_ABORT = False
    if not args.author:
        print("Please give me at least one --author")
        SHOULD_ABORT = True
    if not args.repos:
        print("Please give me at least one --repo")
        SHOULD_ABORT = True

    if SHOULD_ABORT:
        sys.exit(1)

    accumulator = {}
    for author in flatten(args.author):
        for repo in flatten(args.repos):
            dig(accumulator, author, repo, args.branch)
    if not accumulator:
        print("Sorry, I did not find any corresponding commits")
        sys.exit(0)
    weeks = distill_to_weeks(accumulator)
    quarters = distill_to_quarters(accumulator)
    draw_weeks_and_quarters(weeks, quarters, args.output)
    print("You can now open '" + args.output + "' in your browser.")
