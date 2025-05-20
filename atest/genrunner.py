#!/usr/bin/env python

"""Script to generate atest runners based on plain text data files.

Usage:  {tool} testdata/path/data.robot [robot/path/runner.robot]
"""

import os
import re
import sys
from os.path import abspath, basename, dirname, exists, join

if len(sys.argv) not in [2, 3] or not all(a.endswith(".robot") for a in sys.argv[1:]):
    sys.exit(__doc__.format(tool=basename(sys.argv[0])))

SEPARATOR = re.compile(r"\s{2,}|\t")
INPATH = abspath(sys.argv[1])
if join("atest", "testdata") not in INPATH:
    sys.exit("Input not under 'atest/testdata'.")
if len(sys.argv) == 2:
    OUTPATH = INPATH.replace(join("atest", "testdata"), join("atest", "robot"))
else:
    OUTPATH = sys.argv[2]

if not exists(dirname(OUTPATH)):
    os.mkdir(dirname(OUTPATH))


class TestCase:

    def __init__(self, name, tags=None):
        self.name = name
        self.tags = tags


with open(INPATH) as input:
    TESTS = []
    SETTINGS = []
    parsing_tests = False
    parsing_settings = False
    for line in input.readlines():
        line = line.rstrip()
        if not line:
            continue
        elif line.startswith("*"):
            name = SEPARATOR.split(line)[0].replace("*", "").replace(" ", "").upper()
            parsing_tests = name in ("TESTCASES", "TASKS")
            parsing_settings = name == "SETTINGS"
        elif parsing_tests and not SEPARATOR.match(line) and line[0] != "#":
            TESTS.append(TestCase(SEPARATOR.split(line)[0]))
        elif parsing_tests and line.strip().startswith("[Tags]"):
            TESTS[-1].tags = line.split("[Tags]", 1)[1].split()
        elif parsing_settings and line.startswith("Test Tags"):
            name, *values = SEPARATOR.split(line)
            SETTINGS.append((name, values))


with open(OUTPATH, "w") as output:
    path = INPATH.split(join("atest", "testdata"))[1][1:].replace(os.sep, "/")
    output.write(
        f"""\
*** Settings ***
Suite Setup       Run Tests    ${{EMPTY}}    {path}
"""
    )
    for name, values in SETTINGS:
        values = "    ".join(values)
        output.write(f"{name:18}{values}\n")
    output.write(
        """\
Resource          atest_resource.robot

*** Test Cases ***
"""
    )
    for test in TESTS:
        output.write(test.name + "\n")
        if test.tags:
            tags = "    ".join(test.tags)
            output.write(f"    [Tags]    {tags}\n")
        output.write("    Check Test Case    ${TESTNAME}\n")
        if test is not TESTS[-1]:
            output.write("\n")


print(OUTPATH)
