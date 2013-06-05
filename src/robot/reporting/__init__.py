#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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
"""Implements report and log file generation.

Class :class:`~.ResultWriter` is used to write output, log, report
and XUnit files from single :class:`~robot.result.executionresult.Result`
object as well as from one or more existing output.xml files.

:class:`~.ResultWriter` should be imported via :mod:`robot.api`
package:

.. code-block:: python

    from robot.api import ResultWriter

ResultWriter should be imported via robot.api

This package is considered stable.
"""

from .resultwriter import ResultWriter
