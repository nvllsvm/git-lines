#!/usr/bin/env python
import argparse
import json
import os

import git_lines

history = []


def commit_filter(commit):
    global history

    ym = commit.timestamp.strftime('%Y-%m')
    if ym not in history:
        history.append(ym)
        if commit.timestamp.year == 2014 and commit.timestamp.month >= 10:
            return True
        elif commit.timestamp.year > 2014:
            return True

    return False


def blob_filter(blob):
    if blob.name.count('.'):
        extension = blob.name.split('.')[-1]
        if extension in ('php', 'js', 'pl', 'py'):
            return True

    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('repo_directory')
    parser.add_argument('-c', '--cache', required=True)
    args = parser.parse_args()

    if os.path.isfile(args.cache):
        cache = json.load(open(args.cache))
    else:
        cache = None

    cache = git_lines.get_lines(args.repo_directory,
                                commit_filter=commit_filter,
                                blob_filter=blob_filter,
                                cache=cache)

    json.dump(cache, open(args.cache, 'w'))


if __name__ == '__main__':
    main()
