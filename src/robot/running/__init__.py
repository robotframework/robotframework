#  Copyright 2008 Nokia Siemens Networks Oyj
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


from model import TestSuite
from keywords import Keyword
from testlibraries import TestLibrary
from userkeyword import PublicUserLibrary as UserLibrary
from runkwregister import RUN_KW_REGISTER


class _Namespaces:
    
    def __init__(self):
        self._namespaces = []
        self.current = None
        
    def start_suite(self, namespace):
        self._namespaces.append(self.current)
        self.current = namespace
        
    def end_suite(self):
        self.current = self._namespaces.pop()

# Hook to namespaces
NAMESPACES = _Namespaces()
