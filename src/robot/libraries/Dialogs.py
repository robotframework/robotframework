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

"""A library providing dialogs for interacting with users.

``Dialogs`` is Robot Framework's standard library that provides means
for pausing the test or task execution and getting input from users.

Long lines in the provided messages are wrapped automatically. If you want
to wrap lines manually, you can add newlines using the ``\\n`` character
sequence.
"""

from robot.version import get_version

from .dialogs_py import (
    InputDialog, MessageDialog, MultipleSelectionDialog, PassFailDialog, SelectionDialog
)

__version__ = get_version()
__all__ = [
    "execute_manual_step",
    "get_selection_from_user",
    "get_selections_from_user",
    "get_value_from_user",
    "pause_execution",
]


def pause_execution(message: str = "Execution paused. Press OK to continue."):
    """Pauses execution until user clicks ``Ok`` button.

    ``message`` is the message shown in the dialog.
    """
    MessageDialog(message).show()


def execute_manual_step(message: str, default_error: str = ""):
    """Pauses execution until user sets the keyword status.

    User can press either ``PASS`` or ``FAIL`` button. In the latter case execution
    fails and an additional dialog is opened for defining the error message.

    ``message`` is the instruction shown in the initial dialog and
    ``default_error`` is the default value shown in the possible error message
    dialog.
    """
    if not _validate_user_input(PassFailDialog(message)):
        msg = get_value_from_user("Give error message:", default_error)
        raise AssertionError(msg)


def get_value_from_user(
    message: str,
    default_value: str = "",
    hidden: bool = False,
) -> str:
    """Pauses execution and asks user to input a value.

    Value typed by the user, or the possible default value, is returned.
    Returning an empty value is fine, but pressing ``Cancel`` fails the keyword.

    ``message`` is the instruction shown in the dialog and ``default_value`` is
    the possible default value shown in the input field.

    If ``hidden`` is given a true value, the value typed by the user is hidden.
    ``hidden`` is considered true if it is a non-empty string not equal to
    ``false``, ``none`` or ``no``, case-insensitively. If it is not a string,
    its truth value is got directly using same
    [http://docs.python.org/library/stdtypes.html#truth|rules as in Python].

    Example:
    | ${username} = | Get Value From User | Input user name | default    |
    | ${password} = | Get Value From User | Input password  | hidden=yes |
    """
    return _validate_user_input(InputDialog(message, default_value, hidden))


def get_selection_from_user(
    message: str,
    *values: str,
    default: "str | int | None" = None,
) -> str:
    """Pauses execution and asks user to select a value.

    The selected value is returned. Pressing ``Cancel`` fails the keyword.

    ``message`` is the instruction shown in the dialog, ``values`` are
    the options given to the user and ``default`` is the optional default value.

    The default value can either be one of the specified values or the index of
    the value starting from ``1``. For example, ``default=user1`` and ``default=1``
    in the examples below have the exact same effect.

    Example:
    | ${user} = | Get Selection From User | Select user | user1 | user2 | admin |
    | ${user} = | Get Selection From User | Select user | user1 | user2 | admin | default=user1 |
    | ${user} = | Get Selection From User | Select user | user1 | user2 | admin | default=1 |

    ``default`` is new in Robot Framework 7.1.
    """
    return _validate_user_input(SelectionDialog(message, values, default))


def get_selections_from_user(message: str, *values: str) -> "list[str]":
    """Pauses execution and asks user to select multiple values.

    The selected values are returned as a list. Selecting no values is OK
    and in that case the returned list is empty. Pressing ``Cancel`` fails
    the keyword.

    ``message`` is the instruction shown in the dialog and ``values`` are
    the options given to the user.

    Example:
    | ${users} = | Get Selections From User | Select users | user1 | user2 | admin |
    """
    return _validate_user_input(MultipleSelectionDialog(message, values))


def _validate_user_input(dialog):
    value = dialog.show()
    if value is None:
        raise RuntimeError("No value provided by user.")
    return value
