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


from robot import utils
from robot.errors import DataError

from rawdata import RawData
from metadata import ImportSetting
from userkeyword import UserHandlerList


class ResourceFile:
    
    def __init__(self, path, syslog):
        self.path = utils.normpath(path)
        rawdata = RawData(self.path, syslog)
        if rawdata.get_type() != rawdata.RESOURCE:
            self._raise_not_resource(rawdata)
        self.user_keywords = UserHandlerList(rawdata.keywords)
        self.variables = rawdata.variables
        self.imports = []
        self.doc = ''
        for item in rawdata.settings:
            if utils.eq_any(item.name, ['Library', 'Resource', 'Variables']):
                self.imports.append(ImportSetting(item))
            elif utils.eq(item.name, 'Documentation'):
                self.doc = ' '.join(item.value)
            else:
                msg = "Only settings 'Library', 'Resource', 'Variables' and " \
                      + "'Documentation' allowed in resource files. Found: %s"
                item.report_invalid_syntax(msg % item.name)
    
    def _raise_not_resource(self, rawdata):
        if rawdata.get_type() == rawdata.EMPTY:
            msg = "Parsed file '%s' contains no resources"
        else:
            msg = "Parsed file '%s' is not a resource file"
        raise DataError(msg % rawdata.source)
