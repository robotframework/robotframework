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

    def __init__(self, method_or_attr):
        if isinstance(method_or_attr, basestring):
            self.attr_name = method_or_attr
            self.method = None
        else:
            self.attr_name = '___' + method_or_attr.__name__
            self.method = method_or_attr

    def __call__(self, method):
        self.method = method
        return self

    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            return getattr(instance, self.attr_name)
        except AttributeError:
            raise AttributeError(self.method.__name__)

    def __set__(self, instance, value):
        if instance is None:
            return
        setattr(instance, self.attr_name, self.method(instance, value))

