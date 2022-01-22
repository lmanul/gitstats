"Produces a graph showing some statistics in git repositories"

import argparse
import datetime
import sys

from speleologist import dig
from util import date_from_key
from util import date_to_key

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--author", dest="author", action="append", nargs="+",
                        help="The author(s) to look for")
    parser.add_argument("-r", "--repo", dest="repos", action="append", nargs="+",
                        help="The repository(ies) where to look")
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
            dig(accumulator, author, repo)
    weeks = distill_to_weeks(accumulator)
    print(weeks)

    # make_graph(days, weeks)
