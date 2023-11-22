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

"""Exceptions that libraries can use for communicating failures and other events.

These exceptions can be imported also via the top level :mod:`robot.api` package like
``from robot.api import SkipExecution``.

This module and all exceptions are new in Robot Framework 4.0.
"""


class Failure(AssertionError):
    """Report failed validation.

    There is no practical difference in using this exception compared to using
    the standard ``AssertionError``. The main benefits are HTML support and that
    the name of this exception is consistent with other exceptions in this module.
    """
    ROBOT_SUPPRESS_NAME = True

    def __init__(self, message: str, html: bool = False):
        """
        :param message: Exception message.
        :param html: When ``True``, message is considered to be HTML and not escaped.
        """
        super().__init__(message if not html else '*HTML* ' + message)


class ContinuableFailure(Failure):
    """Report failed validation but allow continuing execution."""
    ROBOT_CONTINUE_ON_FAILURE = True


class Error(RuntimeError):
    """Report error in execution.

    Failures related to the system not behaving as expected should typically be
    reported using the :class:`Failure` exception or the standard ``AssertionError``.
    This exception can be used, for example, if the keyword is used incorrectly.

    There is no practical difference in using this exception compared to using
    the standard ``RuntimeError``. The main benefits are HTML support and that
    the name of this exception is consistent with other exceptions in this module.
    """
    ROBOT_SUPPRESS_NAME = True

    def __init__(self, message: str, html: bool = False):
        """
        :param message: Exception message.
        :param html: When ``True``, message is considered to be HTML and not escaped.
        """
        super().__init__(message if not html else '*HTML* ' + message)


class FatalError(Error):
    """Report error that stops the whole execution."""
    ROBOT_EXIT_ON_FAILURE = True
    ROBOT_SUPPRESS_NAME = False


class SkipExecution(Exception):
    """Mark the executed test or task skipped."""
    ROBOT_SKIP_EXECUTION = True
    ROBOT_SUPPRESS_NAME = True

    def __init__(self, message: str, html: bool = False):
        """
        :param message: Exception message.
        :param html: When ``True``, message is considered to be HTML and not escaped.
        """
        super().__init__(message if not html else '*HTML* ' + message)
