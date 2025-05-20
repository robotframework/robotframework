import os
import time


class ListenAll:
    ROBOT_LISTENER_API_VERSION = "2"

    def __init__(self, *path, output_file_disabled=False):
        path = ":".join(path) if path else self._get_default_path()
        self.outfile = open(path, "w", encoding="UTF-8")
        self.output_file_disabled = output_file_disabled
        self.start_attrs = []

    def _get_default_path(self):
        return os.path.join(os.getenv("TEMPDIR"), "listen_all.txt")

    def start_suite(self, name, attrs):
        meta = " ".join(f"{k}: {v}" for k, v in attrs["metadata"].items())
        self.outfile.write(
            f"SUITE START: {name} ({attrs['id']}) '{attrs['doc']}' [{meta}]\n"
        )
        self.start_attrs.append(attrs)

    def start_test(self, name, attrs):
        tags = [str(tag) for tag in attrs["tags"]]
        self.outfile.write(
            f"TEST START: {name} ({attrs['id']}, line {attrs['lineno']}) "
            f"'{attrs['doc']}' {tags}\n"
        )
        self.start_attrs.append(attrs)

    def start_keyword(self, name, attrs):
        if attrs["assign"]:
            assign = ", ".join(attrs["assign"]) + " = "
        else:
            assign = ""
        name = name + " " if name else ""
        if attrs["args"]:
            args = str(attrs["args"]) + " "
        else:
            args = ""
        self.outfile.write(
            f"{attrs['type']} START: {assign}{name}{args}(line {attrs['lineno']})\n"
        )
        self.start_attrs.append(attrs)

    def log_message(self, message):
        msg, level = self._check_message_validity(message)
        if level != "TRACE" and "Traceback" not in msg:
            self.outfile.write(f"LOG MESSAGE: [{level}] {msg}\n")

    def message(self, message):
        msg, level = self._check_message_validity(message)
        if "Settings" in msg:
            self.outfile.write(f"Got settings on level: {level}\n")

    def _check_message_validity(self, message):
        if message["html"] not in ["yes", "no"]:
            self.outfile.write(
                f"Log message has invalid `html` attribute {message['html']}."
            )
        if not message["timestamp"].startswith(str(time.localtime()[0])):
            self.outfile.write(
                f"Log message has invalid timestamp {message['timestamp']}."
            )
        return message["message"], message["level"]

    def end_keyword(self, name, attrs):
        kw_type = "KW" if attrs["type"] == "Keyword" else attrs["type"].upper()
        self.outfile.write(f"{kw_type} END: {attrs['status']}\n")
        self._validate_start_attrs_at_end(attrs)

    def _validate_start_attrs_at_end(self, end_attrs):
        start_attrs = self.start_attrs.pop()
        for key in start_attrs:
            start = start_attrs[key]
            end = end_attrs[key]
            if not (end == start or (key == "status" and start == "NOT SET")):
                raise AssertionError(
                    f"End attr {end!r} is different to " f"start attr {start!r}."
                )

    def end_test(self, name, attrs):
        if attrs["status"] == "PASS":
            self.outfile.write("TEST END: PASS\n")
        else:
            self.outfile.write(f"TEST END: {attrs['status']} {attrs['message']}\n")
        self._validate_start_attrs_at_end(attrs)

    def end_suite(self, name, attrs):
        self.outfile.write(f"SUITE END: {attrs['status']} {attrs['statistics']}\n")
        self._validate_start_attrs_at_end(attrs)

    def output_file(self, path):
        self._out_file("Output", path)

    def report_file(self, path):
        self._out_file("Report", path)

    def log_file(self, path):
        self._out_file("Log", path)

    def xunit_file(self, path):
        self._out_file("Xunit", path)

    def debug_file(self, path):
        self._out_file("Debug", path)

    def _out_file(self, name, path):
        if name == "Output" and self.output_file_disabled:
            if path != "None":
                raise AssertionError(f"Output should be disabled, got {path!r}.")
        else:
            if not (isinstance(path, str) and os.path.isabs(path)):
                raise AssertionError(f"Path should be absolute, got {path!r}.")
            path = os.path.basename(path)
        self.outfile.write(f"{name}: {path}\n")

    def close(self):
        self.outfile.write("Closing...\n")
        self.outfile.close()
