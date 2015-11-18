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

import io

from .platform import PY3


def file_writer(path=None, encoding='UTF-8', newline=None):
    if path:
        f = io.open(path, 'w', encoding=encoding, newline=newline)
    else:
        f = io.StringIO(newline=newline)
    if PY3:
        return f
    # These streams require written text to be Unicode. We don't want to add
    # `u` prefix to all our strings in Python 2, and cannot really use
    # `unicode_literals` either because many other Python 2 APIs accept only
    # byte strings.
    write = f.write
    f.write = lambda text: write(unicode(text))
    return f


def binary_file_writer(path=None):
    if path:
        return io.open(path, 'wb')
    f = io.BytesIO()
    getvalue = f.getvalue
    f.getvalue = lambda encoding='UTF-8': getvalue().decode(encoding)
    return f
