import signal

from robot.api import TestSuite

suite = TestSuite.from_string("""
*** Test Cases ***
Test
    Sleep    ${DELAY}
""").config(name="Suite")  # fmt: skip

signal.signal(signal.SIGALRM, lambda signum, frame: signal.raise_signal(signal.SIGINT))
signal.setitimer(signal.ITIMER_REAL, 1)

result = suite.run(variable="DELAY:5", output=None, log=None, report=None)
assert result.suite.elapsed_time.total_seconds() < 1.5
assert result.suite.status == "FAIL"
result = suite.run(variable="DELAY:0", output=None, log=None, report=None)
assert result.suite.status == "PASS"
