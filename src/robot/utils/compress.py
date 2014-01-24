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

import base64
import sys


def compress_text(text):
    return base64.b64encode(_compress(text.encode('UTF-8')))


if not sys.platform.startswith('java'):

    import zlib

    def _compress(text):
        return zlib.compress(text, 9)

else:
    # Custom compress implementation needed to avoid memory leak:
    # http://bugs.jython.org/issue1775
    # This is based on the zlib.compress in Jython 2.5.2 but has a memory
    # leak fix and is also a little faster.

    from java.util.zip import Deflater
    import jarray

    _DEFLATOR = Deflater(9, False)

    def _compress(text):
        _DEFLATOR.setInput(text)
        _DEFLATOR.finish()
        buf = jarray.zeros(1024, 'b')
        compressed = []
        while not _DEFLATOR.finished():
            length = _DEFLATOR.deflate(buf, 0, 1024)
            compressed.append(buf[:length].tostring())
        _DEFLATOR.reset()
        return ''.join(compressed)
