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

from robot.errors import DataError

from .htmlwriter import LibdocHtmlWriter
from .xmlwriter import LibdocXmlWriter


def LibdocWriter(format=None):
    format = (format or 'HTML').upper()
    if format == 'HTML':
        return LibdocHtmlWriter()
    if format == 'XML':
        return LibdocXmlWriter()
    if format == 'XML:HTML':
        return LibdocXmlWriter(force_html_doc=True)
    raise DataError("Format must be either 'HTML', 'XML' or 'XML:HTML', "
                    "got '%s'." % format)
