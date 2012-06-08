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

import tempfile
import os

from robot.errors import DataError

from .htmlreader import HtmlReader


def RestReader():
    try:
        from docutils.core import publish_cmdline
        from docutils.parsers.rst import directives
    except ImportError:
        raise DataError("Using reStructuredText test data requires having "
                        "'docutils' module installed.")

    # Ignore custom sourcecode directives at least we use in reST sources.
    # See e.g. ug2html.py for an example how custom directives are created.
    ignorer = lambda *args: []
    ignorer.content = 1
    directives.register_directive('sourcecode', ignorer)

    class RestReader(HtmlReader):

        def read(self, rstfile, rawdata):
            htmlpath = self._rest_to_html(rstfile.name)
            htmlfile = None
            try:
                htmlfile = open(htmlpath, 'rb')
                return HtmlReader.read(self, htmlfile, rawdata)
            finally:
                if htmlfile:
                    htmlfile.close()
                os.remove(htmlpath)

        def _rest_to_html(self, rstpath):
            filedesc, htmlpath = tempfile.mkstemp('.html')
            os.close(filedesc)
            publish_cmdline(writer_name='html', argv=[rstpath, htmlpath])
            return htmlpath

    return RestReader()
