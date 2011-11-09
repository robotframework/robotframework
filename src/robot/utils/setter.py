#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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


class setter(object):

    def __init__(self, method):
        self.method = method
        self._method_value_name = '_setter_%s_value' % self.method.__name__

    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            return getattr(instance, self._method_value_name)
        except KeyError:
            raise AttributeError(self.method.__name__)

    def __set__(self, instance, value):
        if instance is None:
            return
        setattr(instance, self._method_value_name, self.method(instance, value))
