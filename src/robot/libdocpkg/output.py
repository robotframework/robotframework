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

import os

from robot.utils import file_writer


class LibdocOutput(object):

    def __init__(self, output_path, format):
        self._output_path = output_path
        self._format = format.upper()
        self._output_file = None

    def __enter__(self):
        if self._format == 'HTML':
            self._output_file = file_writer(self._output_path)
            return self._output_file
        return self._output_path

    def __exit__(self, *exc_info):
        if self._output_file:
            self._output_file.close()
        if any(exc_info):
            os.remove(self._output_path)
