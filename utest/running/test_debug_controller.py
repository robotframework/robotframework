"""Unit tests for the interactive step-debugger controller.

These tests exercise the state machine in ``robot.libraries._debugger``
without opening any Tk windows. A fake dialog factory is injected and
the controller's depth lookup is patched to point at a synthetic
execution context stub so we can simulate arbitrary stack sequences.
"""

import unittest

from robot.errors import ExecutionFailed
from robot.libraries._debugger import (
    ABORT, CONTINUE, STEP_IN, STEP_OUT, STEP_OVER, _DebugController, _DebugListener,
)


class _FakeDialog:
    """Returns a scripted action when ``show()`` is called."""

    def __init__(self, action):
        self._action = action

    def show(self):
        return self._action


class _ScriptedDialogFactory:
    """Pop one ``_FakeDialog`` per ``__call__`` from a scripted queue.

    Used as the ``dialog_factory`` so tests can deterministically drive
    the controller through a sequence of pauses without Tk.
    """

    def __init__(self, actions):
        self._actions = list(actions)
        self.calls = []

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        if not self._actions:
            raise AssertionError("Dialog opened more times than scripted.")
        return _FakeDialog(self._actions.pop(0))


class _StubVariables:

    def as_dict(self, decoration=True):
        return {"${X}": 1}


class _StubContext:

    def __init__(self, depth=0):
        self.steps = [(None, None, None)] * depth
        self.variables = _StubVariables()


def _make_controller(actions, depth_supplier=None):
    """Build a controller wired to a scripted dialog and depth supplier."""
    factory = _ScriptedDialogFactory(actions)
    controller = _DebugController(dialog_factory=factory)
    if depth_supplier is None:
        depth_supplier = lambda ctx=None: 0  # noqa: E731
    controller._current_depth = depth_supplier  # type: ignore[assignment]
    controller._current_context = staticmethod(lambda: _StubContext(0))  # noqa
    controller._gather_stack = lambda ctx: []  # type: ignore[assignment]
    controller._gather_variables = lambda ctx: {}  # type: ignore[assignment]
    return controller, factory


class TestStepPredicate(unittest.TestCase):
    """Pure unit tests on ``_should_stop`` — no dialog interaction."""

    def setUp(self):
        self.controller = _DebugController()

    def test_continue_never_stops(self):
        self.controller._mode = CONTINUE
        self.controller._paused_depth = 5
        for depth in range(0, 10):
            self.assertFalse(self.controller._should_stop(depth))

    def test_step_in_always_stops(self):
        self.controller._mode = STEP_IN
        self.controller._paused_depth = 5
        for depth in range(0, 10):
            self.assertTrue(self.controller._should_stop(depth))

    def test_step_over_stops_at_or_above_paused_depth(self):
        self.controller._mode = STEP_OVER
        self.controller._paused_depth = 5
        self.assertTrue(self.controller._should_stop(5))
        self.assertTrue(self.controller._should_stop(4))
        self.assertTrue(self.controller._should_stop(0))
        self.assertFalse(self.controller._should_stop(6))
        self.assertFalse(self.controller._should_stop(99))

    def test_step_out_stops_only_above_paused_depth(self):
        self.controller._mode = STEP_OUT
        self.controller._paused_depth = 5
        self.assertTrue(self.controller._should_stop(4))
        self.assertTrue(self.controller._should_stop(0))
        self.assertFalse(self.controller._should_stop(5))
        self.assertFalse(self.controller._should_stop(6))
        self.assertFalse(self.controller._should_stop(99))


class TestHandleAction(unittest.TestCase):
    """Verify state transitions chosen by the user via the dialog."""

    def setUp(self):
        self.controller = _DebugController()

    def test_unknown_action_falls_back_to_continue(self):
        self.controller._mode = STEP_IN
        self.controller._paused_depth = 7
        self.controller._handle_action(None, depth=3)
        self.assertEqual(self.controller._mode, CONTINUE)
        self.assertEqual(self.controller._paused_depth, 0)

    def test_step_in_records_depth(self):
        self.controller._handle_action(STEP_IN, depth=3)
        self.assertEqual(self.controller._mode, STEP_IN)
        self.assertEqual(self.controller._paused_depth, 3)

    def test_step_over_records_depth(self):
        self.controller._handle_action(STEP_OVER, depth=4)
        self.assertEqual(self.controller._mode, STEP_OVER)
        self.assertEqual(self.controller._paused_depth, 4)

    def test_step_out_records_depth(self):
        self.controller._handle_action(STEP_OUT, depth=5)
        self.assertEqual(self.controller._mode, STEP_OUT)
        self.assertEqual(self.controller._paused_depth, 5)

    def test_continue_resets_state(self):
        self.controller._mode = STEP_OVER
        self.controller._paused_depth = 9
        self.controller._handle_action(CONTINUE, depth=2)
        self.assertEqual(self.controller._mode, CONTINUE)
        self.assertEqual(self.controller._paused_depth, 0)

    def test_abort_raises_execution_failed(self):
        with self.assertRaises(ExecutionFailed) as cm:
            self.controller._handle_action(ABORT, depth=2)
        self.assertTrue(cm.exception.exit)
        self.assertEqual(self.controller._mode, CONTINUE)
        self.assertEqual(self.controller._paused_depth, 0)


class TestEndToEndStepping(unittest.TestCase):
    """Drive `pause()` + subsequent `on_start_body_item` events.

    Each test fixes the depth visible to the controller at every call,
    scripts the dialog actions, and asserts how many extra pauses are
    triggered as the simulated execution proceeds.
    """

    def _run(self, *, paused_depth, actions, event_depths):
        """Helper: pause at ``paused_depth`` then replay event depths.

        Returns the number of dialog opens after the initial pause.
        """
        current_depth = paused_depth

        def depth_supplier(ctx=None):
            return current_depth

        controller, factory = _make_controller(actions, depth_supplier)
        controller.pause("paused")
        for depth in event_depths:
            current_depth = depth
            controller.on_start_body_item(data=None, result=None)
        return len(factory.calls) - 1

    def test_continue_stops_only_on_explicit_pause(self):
        extra_pauses = self._run(
            paused_depth=5,
            actions=[CONTINUE],
            event_depths=[3, 4, 5, 6, 7, 8, 5],
        )
        self.assertEqual(extra_pauses, 0)

    def test_step_in_stops_on_very_next_event(self):
        extra_pauses = self._run(
            paused_depth=5,
            actions=[STEP_IN, CONTINUE],
            event_depths=[6, 7, 8],
        )
        self.assertEqual(extra_pauses, 1)

    def test_step_over_skips_deeper_calls(self):
        extra_pauses = self._run(
            paused_depth=5,
            actions=[STEP_OVER, CONTINUE],
            event_depths=[6, 7, 8, 5],
        )
        self.assertEqual(extra_pauses, 1)

    def test_step_over_stops_after_returning_to_shallower(self):
        extra_pauses = self._run(
            paused_depth=5,
            actions=[STEP_OVER, CONTINUE],
            event_depths=[6, 7, 4],
        )
        self.assertEqual(extra_pauses, 1)

    def test_step_out_ignores_same_and_deeper_depths(self):
        extra_pauses = self._run(
            paused_depth=5,
            actions=[STEP_OUT, CONTINUE],
            event_depths=[5, 6, 5, 7, 5, 4],
        )
        self.assertEqual(extra_pauses, 1)

    def test_chained_step_in_pauses_every_event(self):
        extra_pauses = self._run(
            paused_depth=5,
            actions=[STEP_IN, STEP_IN, STEP_IN, CONTINUE],
            event_depths=[6, 7, 7, 6, 5],
        )
        self.assertEqual(extra_pauses, 3)

    def test_step_in_then_step_over_at_new_depth(self):
        extra_pauses = self._run(
            paused_depth=5,
            actions=[STEP_IN, STEP_OVER, CONTINUE],
            event_depths=[6, 7, 8, 6, 7],
        )
        self.assertEqual(extra_pauses, 2)


class TestFormatValue(unittest.TestCase):
    """The variables panel formatter must be robust to weird values."""

    def test_long_value_is_truncated(self):
        formatted = _DebugController._format_value("x" * 500)
        self.assertTrue(formatted.endswith("..."))
        self.assertLessEqual(len(formatted), 210)

    def test_unrepresentable_value_does_not_crash(self):
        class _Bad:
            def __repr__(self):
                raise RuntimeError("nope")

        formatted = _DebugController._format_value(_Bad())
        self.assertTrue(formatted.startswith("<unrepresentable"), formatted)


class TestReentrancy(unittest.TestCase):
    """Verify the controller cannot recurse into a second dialog while
    one is already open. Should not normally happen (the dialog blocks
    the runner thread), but the guard protects against custom dialog
    implementations that run nested event loops calling back into RF.
    """

    def test_reentrant_event_is_ignored(self):
        controller, factory = _make_controller([CONTINUE])
        controller._in_dialog = True
        controller._mode = STEP_IN
        controller._paused_depth = 0
        controller.on_start_body_item(data=None, result=None)
        self.assertEqual(len(factory.calls), 0)


class TestListenerForwarding(unittest.TestCase):
    """``_DebugListener.start_body_item`` must forward to the controller."""

    def test_forwarding(self):
        captured = []

        class _Recorder:
            def on_start_body_item(self, data, result):
                captured.append((data, result))

        listener = _DebugListener(_Recorder())
        listener.start_body_item("d", "r")
        self.assertEqual(captured, [("d", "r")])

    def test_keyword_callbacks_funnel_through_body_item(self):
        captured = []

        class _Recorder:
            def on_start_body_item(self, data, result):
                captured.append(result)

        listener = _DebugListener(_Recorder())
        listener.start_user_keyword(data="d", implementation="i", result="r")
        listener.start_library_keyword(data="d2", implementation="i", result="r2")
        listener.start_for(data="d3", result="r3")
        listener.start_if_branch(data="d4", result="r4")
        self.assertEqual(captured, ["r", "r2", "r3", "r4"])


if __name__ == "__main__":
    unittest.main()
