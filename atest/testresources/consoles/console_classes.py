"""Module with a differently-named console class for dotted import testing."""
import sys


class MyConsole:

    def __init__(self, marker='DOTTED'):
        self.marker = marker

    def start_suite(self, data, result):
        sys.__stdout__.write(f"{self.marker}: Suite '{result.name}' started\n")

    def end_test(self, data, result):
        sys.__stdout__.write(f"{self.marker}: Test '{result.name}' {result.status}\n")

    def output_file(self, path):
        sys.__stdout__.write(f"{self.marker}: Output: {path}\n")

    def close(self):
        sys.__stdout__.write(f"{self.marker}: Closing\n")
