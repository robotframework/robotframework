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

from robot.htmldata import HtmlFileWriter, ModelWriter, LIBDOC


class LibdocHtmlWriter:

    def __init__(self, theme=None):
        self.theme = theme

    def write(self, libdoc, output):
        model_writer = LibdocModelWriter(output, libdoc, self.theme)
        HtmlFileWriter(output, model_writer).write(LIBDOC)


class LibdocModelWriter(ModelWriter):

    def __init__(self, output, libdoc, theme=None):
        self.output = output
        self.libdoc = libdoc
        self.theme = theme

    def write(self, line):
        data = self.libdoc.to_json(include_private=False, theme=self.theme)
        self.output.write(f'<script type="text/javascript">\n'
                          f'libdoc = {data}\n'
                          f'</script>\n')
