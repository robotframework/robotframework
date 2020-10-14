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

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote

from robot.htmldata import HtmlFileWriter, ModelWriter, JsonWriter, LIBDOC


class LibdocHtmlWriter(object):

    def write(self, libdoc, output):
        model_writer = LibdocModelWriter(output, libdoc)
        HtmlFileWriter(output, model_writer).write(LIBDOC)


class LibdocModelWriter(ModelWriter):

    def __init__(self, output, libdoc):
        self._output = output
        libdoc.convert_doc_to_html()
        self._libdoc = libdoc.to_dictionary()

    def write(self, line):
        self._output.write('<script type="text/javascript">\n')
        self.write_data()
        self._output.write('</script>\n')

    def write_data(self):
        JsonWriter(self._output).write_json('libdoc = ', self._libdoc)
