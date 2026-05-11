import sys


class CustomConsole:

    def __init__(self, marker="CUSTOM"):
        self.marker = marker

    def start_suite(self, data, result):
        sys.__stdout__.write(f"{self.marker}: Suite '{result.name}' started\n")

    def end_test(self, data, result):
        sys.__stdout__.write(f"{self.marker}: Test '{result.name}' {result.status}\n")

    def message(self, msg):
        if msg.level in ("WARN", "ERROR"):
            sys.__stdout__.write(f"{self.marker} {msg.level}: {msg.message}\n")

    def output_file(self, path):
        sys.__stdout__.write(f"{self.marker}: Output: {path}\n")

    def report_file(self, path):
        sys.__stdout__.write(f"{self.marker}: Report: {path}\n")

    def log_file(self, path):
        sys.__stdout__.write(f"{self.marker}: Log: {path}\n")

    def close(self):
        sys.__stdout__.write(f"{self.marker}: Closing\n")
