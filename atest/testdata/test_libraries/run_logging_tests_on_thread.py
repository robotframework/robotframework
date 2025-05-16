import sys
from pathlib import Path
from threading import Thread

CURDIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(CURDIR / "../../../src"))
sys.path.insert(1, str(CURDIR / "../../testresources/testlibs"))


from robot import run  # noqa: E402


def run_logging_tests(output):
    run(
        CURDIR / "logging_api.robot",
        CURDIR / "logging_with_logging.robot",
        CURDIR / "print_logging.robot",
        name="Logging tests",
        dotted=True,
        output=output,
        report=None,
        log=None,
    )


output = (*sys.argv, "output.xml")[1]
t = Thread(target=lambda: run_logging_tests(output))
t.start()
t.join()
