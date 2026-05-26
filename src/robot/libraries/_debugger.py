#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Interactive step-debugger backing the ``Debug`` keyword in Dialogs.

This module is internal. Public surface is the ``Debug`` keyword in
``robot.libraries.Dialogs``. The implementation is split into two pieces:

* :class:`_DebugController` — singleton holding the step state machine
  (paused depth + step mode), opens a UI dialog when paused, and decides
  on each subsequent step whether to pause again.
* :class:`_DebugListener` — minimal :class:`LoggerApi` subclass that
  forwards every ``start_body_item`` event to the controller. Registered
  lazily through ``LOGGER.register_logger`` the first time the user
  activates the debugger so that simply importing the ``Dialogs`` library
  has no side effects.

Stepping semantics use stack depth tracked via
``EXECUTION_CONTEXTS.current.steps``:

* ``STEP_IN``  — stop on the very next body item, any depth.
* ``STEP_OVER`` — stop when ``depth <= paused_depth`` (next sibling or
  after returning to a shallower scope).
* ``STEP_OUT`` — stop when ``depth < paused_depth`` (only after returning
  from the current scope).
* ``CONTINUE`` — never stop until the user hits another ``Debug`` keyword.
* ``ABORT`` — raise ``ExecutionFailed(..., exit=True)`` to gracefully end
  the run.

The controller is deliberately UI-agnostic. The dialog factory is
injectable so unit tests can drive the state machine without Tk.
The Variables panel is read-only — to inspect a value at a pause
point, bind it to a variable (or call ``Log`` / ``Log Variables``)
before the ``Debug`` call.
"""

from robot.errors import ExecutionFailed
from robot.output.loggerapi import LoggerApi


CONTINUE = "CONTINUE"
STEP_IN = "STEP_IN"
STEP_OVER = "STEP_OVER"
STEP_OUT = "STEP_OUT"
ABORT = "ABORT"

_VALID_ACTIONS = frozenset((CONTINUE, STEP_IN, STEP_OVER, STEP_OUT, ABORT))


class _DebugController:
    """Singleton state machine for the interactive step debugger.

    Use :meth:`instance` to access the shared instance. Tests can create
    additional instances directly and inject a fake ``dialog_factory`` to
    avoid opening Tk windows.
    """

    _instance = None

    def __init__(self, dialog_factory=None):
        self._mode = CONTINUE
        self._paused_depth = 0
        self._listener = None
        self._listener_registered = False
        self._dialog_factory = dialog_factory
        self._in_dialog = False

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Test hook: drop the cached singleton."""
        if cls._instance is not None and cls._instance._listener_registered:
            try:
                from robot.output.logger import LOGGER

                LOGGER.unregister_logger(cls._instance._listener)
            except Exception:
                pass
        cls._instance = None

    def pause(self, message):
        """Open the debugger dialog from inside the ``Debug`` keyword.

        ``message`` is shown in the dialog header. This call blocks until
        the user picks an action.
        """
        self._ensure_listener()
        self._open_dialog(message=message, kind="paused")

    def on_start_body_item(self, data, result):
        if self._mode == CONTINUE:
            return
        if self._in_dialog:
            return
        depth = self._current_depth()
        if self._should_stop(depth):
            self._open_dialog(
                message=self._format_step_message(data, result),
                kind="step",
            )

    def _should_stop(self, depth):
        if self._mode == STEP_IN:
            return True
        if self._mode == STEP_OVER:
            return depth <= self._paused_depth
        if self._mode == STEP_OUT:
            return depth < self._paused_depth
        return False

    def _open_dialog(self, message, kind):
        snapshot = self._snapshot()
        depth = snapshot["depth"]
        dialog_factory = self._dialog_factory or self._default_dialog_factory
        self._in_dialog = True
        try:
            dialog = dialog_factory(
                message=message,
                stack=snapshot["stack"],
                variables=snapshot["variables"],
                kind=kind,
            )
            action = dialog.show()
        finally:
            self._in_dialog = False
        self._handle_action(action, depth)

    def _handle_action(self, action, depth):
        if action not in _VALID_ACTIONS:
            action = CONTINUE
        if action == STEP_IN:
            self._mode = STEP_IN
            self._paused_depth = depth
        elif action == STEP_OVER:
            self._mode = STEP_OVER
            self._paused_depth = depth
        elif action == STEP_OUT:
            self._mode = STEP_OUT
            self._paused_depth = depth
        elif action == CONTINUE:
            self._mode = CONTINUE
            self._paused_depth = 0
        elif action == ABORT:
            self._mode = CONTINUE
            self._paused_depth = 0
            raise ExecutionFailed(
                "Test execution aborted from debugger.",
                exit=True,
            )

    def _snapshot(self):
        ctx = self._current_context()
        return {
            "depth": self._current_depth(ctx),
            "stack": self._gather_stack(ctx),
            "variables": self._gather_variables(ctx),
        }

    @staticmethod
    def _current_context():
        from robot.running.context import EXECUTION_CONTEXTS

        return EXECUTION_CONTEXTS.current

    def _current_depth(self, ctx=None):
        if ctx is None:
            ctx = self._current_context()
        if ctx is None:
            return 0
        return len(ctx.steps)

    def _gather_stack(self, ctx):
        if ctx is None:
            return []
        frames = []
        for data, result, implementation in ctx.steps:
            frames.append(self._format_frame(data, result, implementation))
        return frames

    def _gather_variables(self, ctx):
        if ctx is None:
            return {}
        try:
            variables = ctx.variables.as_dict(decoration=True)
        except Exception:
            return {}
        return {name: self._format_value(value) for name, value in variables.items()}

    @staticmethod
    def _format_value(value):
        try:
            text = repr(value)
        except Exception as err:
            return f"<unrepresentable: {err}>"
        if len(text) > 200:
            text = text[:197] + "..."
        return text

    @staticmethod
    def _format_frame(data, result, implementation):
        kind = getattr(result, "type", "") or ""
        name = _DebugController._body_item_label(data, result, implementation)
        if kind:
            return f"{kind}: {name}"
        return name

    def _format_step_message(self, data, result):
        kind = getattr(result, "type", "") or "STEP"
        name = _DebugController._body_item_label(data, result, None)
        return f"Stepping into {kind}: {name}"

    @staticmethod
    def _body_item_label(data, result, implementation):
        """Best-effort short label for a body item / result pair.

        Avoids reading `.name` on result objects because that property
        is deprecated on control-structure result classes (For, While,
        Return, If, Try, etc.) and emits a UserWarning every time it is
        touched in Robot Framework 7.x. ``str(data)`` is the public,
        non-deprecated way to get a human-readable representation of
        any body item.
        """
        if implementation is not None:
            full_name = getattr(implementation, "full_name", None)
            if full_name:
                return full_name
        try:
            text = str(data)
        except Exception:
            text = ""
        if text:
            return text
        return type(result).__name__

    def _ensure_listener(self):
        if self._listener_registered:
            return
        from robot.output.logger import LOGGER

        self._listener = _DebugListener(self)
        LOGGER.register_logger(self._listener)
        self._listener_registered = True

    @staticmethod
    def _default_dialog_factory(message, stack, variables, kind):
        from .dialogs_debugger import DebuggerDialog

        return DebuggerDialog(
            message=message,
            stack=stack,
            variables=variables,
            kind=kind,
        )


class _DebugListener(LoggerApi):
    """Minimal logger that fires the debugger predicate on every step.

    Inherits :class:`LoggerApi` so every concrete ``start_*`` callback
    funnels through :meth:`start_body_item` by default. Errors raised
    here are surfaced to the runner (``LOGGER`` does not swallow logger
    exceptions), so the controller must not raise except for an
    intentional :class:`ExecutionFailed` from ``ABORT``.
    """

    def __init__(self, controller):
        self._controller = controller

    def start_body_item(self, data, result):
        self._controller.on_start_body_item(data, result)
