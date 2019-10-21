#!/usr/bin/env python

"""Script to extract examples from library docs to ease testing them.

Usage: extract_examples.py path_to_lib
"""

import os.path
import sys


def extract_tests(path):
    initialize(path)
    read_tests(path)


def initialize(path):
    lib = os.path.splitext(os.path.basename(path))[0]
    print("""\
*** Settings ***
Library    %s

*** Test Cases ***\
""" % lib)


def read_tests(path):
    test = '????'

    for line in open(path):
        line = line.strip()
        if line.startswith('='):
            test = line.strip('= ')
        if line.startswith('def'):
            test = line[4:].split('(')[0]
        if line.startswith('|') and line.endswith('|') and len(line) > 1:
            if test:
                print('\n', test)
                test = None
            print('|    ' + line)


if __name__ == '__main__':
    try:
        path = sys.argv[1]
    except IndexError:
        print(__doc__)
    else:
        extract_tests(path)
