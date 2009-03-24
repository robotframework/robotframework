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


from robot.parsing import ResourceFile
from robot.output import SYSLOG
from robot import utils

from testlibraries import TestLibrary
from userkeyword import UserLibrary


class Importer:

    def __init__(self):
        self._libraries = {}
        self._resources = {}
        
    def import_library(self, name, args):
        key = (name, tuple(args))
        if self._libraries.has_key(key):
            SYSLOG.info("Found test library '%s' with arguments %s from cache" 
                        % (name, utils.seq2str2(args)))
        else:
            lib = TestLibrary(name, args)
            self._libraries[key] = lib
            libtype = lib.__class__.__name__.replace('Library', '').lower()[1:]
            SYSLOG.info("Imported library '%s' with arguments %s (version %s, "
                        "%s type, %s scope, %d keywords, source %s)" 
                        % (name, utils.seq2str2(args), lib.version, libtype, 
                           lib.scope.lower(), len(lib), lib.source))
            if len(lib) == 0:
                SYSLOG.warn("Imported library '%s' contains no keywords" % name)
        return self._libraries[key]
    
    def import_resource(self, path):
        if self._resources.has_key(path):
            SYSLOG.info("Found resource file '%s' from cache" % path)
        else:
            resource = ResourceFile(path)
            resource.user_keywords = UserLibrary(resource.user_keywords, path)
            self._resources[path] = resource
            SYSLOG.info("Imported resource file '%s' (%d keywords)" 
                        % (path, len(resource.user_keywords)))
            # Resource file may contain only variables so we should not warn
            # if there are no keywords. Importing an empty resource file fails
            # already earlier so no need to check that here either.
        return self._resources[path]
 
