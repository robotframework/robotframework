"""Listener for validation result files using the v3 API.

ListenAll.py has same validation, among other things, using the v2 API.
"""


class ResultFiles:

    def __init__(self, path, output_file_disabled=False, only_result_file=False):
        self.outfile = open(path, "w", encoding="UTF-8")
        self.output_file_disabled = output_file_disabled
        if only_result_file:
            self.output_file = None
            self.report_file = None
            self.log_file = None
            self.xunit_file = None
            self.debug_file = None

    def output_file(self, path):
        self._result_file("Output", path, output=True)

    def report_file(self, path):
        self._result_file("Report", path)

    def log_file(self, path):
        self._result_file("Log", path)

    def xunit_file(self, path):
        self._result_file("Xunit", path)

    def debug_file(self, path):
        self._result_file("Debug", path)

    def result_file(self, kind, path):
        if kind not in ["OUTPUT", "REPORT", "LOG", "XUNIT", "DEBUG"]:
            raise AssertionError(f"Invalid result file type '{kind}'.")
        self._result_file(kind, path, output=kind == "OUTPUT")

    def _result_file(self, kind, path, output=False):
        if output and self.output_file_disabled:
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
