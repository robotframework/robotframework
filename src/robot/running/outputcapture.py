#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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

import sys
from StringIO import StringIO


class OutputCapturer:

    def __init__(self):
        self._python_output = _PythonOutput()
        self._java_output = _JavaOutput()

    def release(self):
        pyout, pyerr = self._python_output.release()
        jaout, jaerr = self._java_output.release()
        return (pyout, pyerr) if pyout or pyerr else (jaout, jaerr)


class _PythonOutput(object):

    def __init__(self):
        self._orig_out = sys.stdout
        self._orig_err = sys.stderr
        sys.stderr = StringIO()
        sys.stdout = StringIO()

    def release(self):
        sys.stdout.flush()
        sys.stderr.flush()
        out = sys.stdout.getvalue()
        err = sys.stderr.getvalue()
        sys.stdout = self._orig_out
        sys.stderr = self._orig_err
        return out, err


if not sys.platform.startswith('java'):
    class _JavaOutput(object):
        def release(self):
            return '', ''

else:
    from java.io import PrintStream, ByteArrayOutputStream
    from java.lang import System
    
    class _JavaOutput(object):
        
        def __init__(self):
            self._orig_out = System.out
            self._orig_err = System.err
            self._out = ByteArrayOutputStream()
            self._err = ByteArrayOutputStream()
            System.setOut(PrintStream(self._out, False, 'UTF-8'))
            System.setErr(PrintStream(self._err, False, 'UTF-8'))
    
        def release(self):
            System.out.close()
            System.err.close()
            System.setOut(self._orig_out)
            System.setErr(self._orig_err)
            return self._out.toString('UTF-8'), self._err.toString('UTF-8')
