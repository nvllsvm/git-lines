#!/usr/bin/env python
import argparse
import json
import os
import subprocess
from datetime import datetime


class Repo(object):
    def __init__(self, directory):
        self.directory = directory

    def get_commits(self):
        cmd = 'git log --pretty=format:"%at %T %H" HEAD'

        for line in run_command(cmd, cwd=self.directory):
            unix_timestamp, tree, commit = line.split()
            timestamp = datetime.fromtimestamp(int(unix_timestamp))
            yield Commit(self.directory, commit, tree, timestamp)


class Commit(object):
    def __init__(self, directory, commit, tree, timestamp):
        self.commit = commit
        self.tree = tree
        self.timestamp = timestamp
        self.directory = directory

    def get_blobs(self):
        cmd = 'git ls-tree -r {}'.format(self.tree)

        for line in run_command(cmd, cwd=self.directory):
            _, object_type, blob, name = line.split(None, 3)
            if object_type == 'blob':
                yield Blob(self.directory, blob, name)


class Blob(object):
    def __init__(self, directory, blob, name):
        self.directory = directory
        self.blob = blob
        self.name = name

    @property
    def num_lines(self):
        cmd = 'git cat-file blob {} | wc -l'.format(self.blob)
        output = run_command(cmd, cwd=self.directory)
        return int(output[0])


def run_command(cmd, cwd=None):
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, shell=True)
    output, errors = p.communicate()
    p.wait()

    output = [o for o in output.decode("utf-8").split('\n') if o]

    return output


def get_lines(repo_directory, cache=None,
              commit_filter=None, blob_filter=None):
    if not cache:
        cache = {}

    repo = Repo(repo_directory)

    for commit in repo.get_commits():
        if commit_filter and not commit_filter(commit):
            continue

        lines = 0
        for blob in commit.get_blobs():
            if blob_filter and not blob_filter(blob):
                continue

            if blob.blob not in cache.keys():
                cache[blob.blob] = blob.num_lines

            lines += cache[blob.blob]

        print('{} {} {} {}'.format(commit.timestamp.strftime('%Y-%m-%d'),
                                   commit.timestamp.strftime('%H:%M:%S'),
                                   commit.commit,
                                   lines))

    return cache


def main():
    parser = argparse.ArgumentParser(
            description='Total lines throughout a git repo\'s history')
    parser.add_argument('repo_directory')
    parser.add_argument('-c', '--cache')
    args = parser.parse_args()

    if args.cache and os.path.isfile(args.cache):
        cache = get_lines(args.repo_directory,
                          cache=json.load(open(args.cache)))
    else:
        cache = get_lines(args.repo_directory)

    if args.cache:
        json.dump(cache, open(args.cache, 'w'))


if __name__ == '__main__':
    main()
