#  Copyright 2008-2015 Nokia Solutions and Networks
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

"""Package for writing output files in HTML format.

This package is considered stable but it is not part of the public API.
"""

from .htmlfilewriter import HtmlFileWriter, ModelWriter
from .jsonwriter import JsonWriter

LOG = 'rebot/log.html'
REPORT = 'rebot/report.html'
LIBDOC = 'libdoc/libdoc.html'
TESTDOC = 'testdoc/testdoc.html'
