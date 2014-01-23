#  Copyright 2008-2014 Nokia Solutions and Networks
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

from cStringIO import StringIO

from .htmlreader import HtmlReader
from .txtreader import TxtReader


def RestReader():
    from .restsupport import (publish_doctree, publish_from_doctree,
                              RobotDataStorage)

    class RestReader(object):

        def read(self, rstfile, rawdata):
            doctree = publish_doctree(
                rstfile.read(), source_path=rstfile.name,
                settings_overrides={'input_encoding': 'UTF-8'})
            store = RobotDataStorage(doctree)
            if store.has_data():
                return self._read_text(store.get_data(), rawdata)
            return self._read_html(doctree, rawdata)

        def _read_text(self, data, rawdata):
            txtfile = StringIO(data.encode('UTF-8'))
            return TxtReader().read(txtfile, rawdata)

        def _read_html(self, doctree, rawdata):
            htmlfile = StringIO()
            htmlfile.write(publish_from_doctree(
                doctree, writer_name='html',
                settings_overrides={'output_encoding': 'UTF-8'}))
            htmlfile.seek(0)
            return HtmlReader().read(htmlfile, rawdata)

    return RestReader()
