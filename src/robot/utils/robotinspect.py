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

from .platform import JYTHON


if JYTHON:

    from org.python.core import PyReflectedFunction, PyReflectedConstructor

    def is_java_init(init):
        return isinstance(init, PyReflectedConstructor)

    def is_java_method(method):
        func = method.im_func if hasattr(method, 'im_func') else method
        return isinstance(func, PyReflectedFunction)

else:

    def is_java_init(init):
        return False

    def is_java_method(method):
        return False
