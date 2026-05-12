import sys


class CustomConsole:

    def __init__(self, name="DEFAULT"):
        self.name = name

    def write(self, message):
        print(message, file=sys.__stdout__)

    def start_suite(self, data, result):
        self.write(f"{self.name}: Suite '{result.name}' started")

    def end_test(self, data, result):
        self.write(f"{self.name}: Test '{result.name}' {result.status}")

    def message(self, msg):
        if msg.level in ("WARN", "ERROR"):
            self.write(f"{self.name} {msg.level}: {msg.message}")

    def output_file(self, path):
        self.write(f"{self.name}: Output: {path}")

    def report_file(self, path):
        self.write(f"{self.name}: Report: {path}")

    def log_file(self, path):
        self.write(f"{self.name}: Log: {path}")

    def close(self):
        self.write(f"{self.name}: Closing")
