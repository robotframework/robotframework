#  Copyright 2020-     Robot Framework Foundation
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

import json

from robot.utils import file_writer


class LibdocJsonWriter(object):

    def __init__(self, spec_doc_format):
        self._spec_doc_format = spec_doc_format

    def write(self, libdoc, outfile):
        if self._spec_doc_format == 'HTML':
            libdoc.convert_doc_to_html()
        with file_writer(outfile) as f:
            json.dump(libdoc.to_dictionary(), f, indent=2)
