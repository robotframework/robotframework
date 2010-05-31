#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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


from robot.output import XmlLogger


class OutputSerializer(XmlLogger):

    def __init__(self, outpath, split):
        XmlLogger.__init__(self, outpath, 'TRACE', split, generator='Rebot')

    def message(self, msg):
        self._message(msg)

    def start_errors(self, errors):
        XmlLogger.start_errors(self)

    def end_errors(self, errors):
        XmlLogger.end_errors(self)
