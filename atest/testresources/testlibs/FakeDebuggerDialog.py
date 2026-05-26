"""Test library that swaps the real Tk dialog used by the ``Debug``
keyword for a scripted fake so that ``standard_libraries/dialogs``
acceptance tests can run non-interactively on CI.

Usage from a Robot test:

| Library    FakeDebuggerDialog
|
| *** Test Cases ***
| Step in and continue
|     Script Debugger Actions    STEP_IN    CONTINUE
|     Debug                       Pause here
|     Some Keyword
|     Debugger Open Count Should Be    2
"""

from robot.libraries import _debugger
from robot.libraries._debugger import _DebugController


class _ScriptedFakeDialog:

    def __init__(self, controller, action):
        self._controller = controller
        self._action = action

    def show(self):
        return self._action


class _Recorder:

    def __init__(self):
        self.actions = []
        self.calls = []

    def factory(self, message, stack, variables, kind):
        self.calls.append(
            {"message": message, "kind": kind, "stack": list(stack)}
        )
        if not self.actions:
            action = _debugger.CONTINUE
        else:
            action = self.actions.pop(0)
        return _ScriptedFakeDialog(self, action)


class FakeDebuggerDialog:
    """Robot library exposing scripting helpers for the debugger dialog."""

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    _ACTIONS = {
        "STEP_IN": _debugger.STEP_IN,
        "STEP_OVER": _debugger.STEP_OVER,
        "STEP_OUT": _debugger.STEP_OUT,
        "CONTINUE": _debugger.CONTINUE,
        "ABORT": _debugger.ABORT,
    }

    def __init__(self):
        self._recorder = _Recorder()
        self._installed = False

    def script_debugger_actions(self, *actions):
        """Set the sequence of actions the next dialog opens will return.

        ``actions`` is a list of strings, one per pause: ``STEP_IN``,
        ``STEP_OVER``, ``STEP_OUT``, ``CONTINUE`` or ``ABORT``.
        """
        self._install_factory()
        self._recorder.actions = [self._resolve(a) for a in actions]
        self._recorder.calls = []

    def _resolve(self, name):
        try:
            return self._ACTIONS[name.upper()]
        except KeyError:
            raise ValueError(
                f"Unknown debugger action '{name}'. "
                f"Expected one of: {', '.join(self._ACTIONS)}."
            )

    def _install_factory(self):
        if self._installed:
            return
        _DebugController.instance()._dialog_factory = self._recorder.factory
        self._installed = True

    def debugger_open_count_should_be(self, expected):
        """Assert how many times the (fake) debugger dialog has opened."""
        actual = len(self._recorder.calls)
        expected = int(expected)
        if actual != expected:
            raise AssertionError(
                f"Expected debugger dialog to open {expected} times, "
                f"got {actual}. Calls: {self._recorder.calls}"
            )

    def get_debugger_call_messages(self):
        """Return the list of headline messages from each dialog open."""
        return [call["message"] for call in self._recorder.calls]

    def reset_debugger(self):
        """Reset both the recorder state and the controller singleton.

        Call this from Suite Teardown so other tests aren't affected.
        """
        self._recorder.actions = []
        self._recorder.calls = []
        _DebugController.reset_instance()
        self._installed = False
