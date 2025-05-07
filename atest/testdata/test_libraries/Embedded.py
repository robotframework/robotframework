from robot.api.deco import keyword


class Embedded:

    def __init__(self):
        self.called = 0

    @keyword("Called ${times} time(s)", types={"times": int})
    def called_times(self, times):
        self.called += 1
        if self.called != times:
            raise AssertionError(
                f"Called {self.called} time(s), expected {times} time(s)."
            )
