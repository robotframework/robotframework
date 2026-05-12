"""Listener for validation result files using the v3 API.

ListenAll.py has same validation, among other things, using the v2 API.
"""


class ResultFiles:

    def __init__(self, path, output_file_disabled=False):
        self.outfile = open(path, "w", encoding="UTF-8")
        self.output_file_disabled = output_file_disabled

    def output_file(self, path):
        self._result_file("Output", path)

    def report_file(self, path):
        self._result_file("Report", path)

    def log_file(self, path):
        self._result_file("Log", path)

    def xunit_file(self, path):
        self._result_file("Xunit", path)

    def debug_file(self, path):
        self._result_file("Debug", path)

    def _result_file(self, kind, path):
        if kind == "Output" and self.output_file_disabled:
            if path is not None:
                raise AssertionError(f"Output should be disabled, got {path!r}.")
            name = "None"
        else:
            if not path.is_absolute():
                raise AssertionError(f"Path should be absolute, got {path!r}.")
            name = path.name
        self.write(f"{kind}: {name}")

    def write(self, message):
        self.outfile.write(message + "\n")

    def close(self):
        self.write("Closing...")
        self.outfile.close()
