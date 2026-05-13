"""Module-level console with no class — bare functions.

Does not define output_file/report_file/log_file, so result file
paths are suppressed (the V3 facade treats missing methods as no-ops).
"""

import sys

MARKER = "MODULE"


def start_suite(data, result):
    sys.__stdout__.write(f"{MARKER}: Suite '{result.name}' started\n")


def end_test(data, result):
    sys.__stdout__.write(f"{MARKER}: Test '{result.name}' {result.status}\n")


def close():
    sys.__stdout__.write(f"{MARKER}: Closing\n")
