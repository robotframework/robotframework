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


# import inspect


class importvalidator(object):
    ROBOT_LISTENER_API_VERSION = 2
    used_imports = set()
    imported = set()

    def start_suite(self, suite, attrs):
        # print('ImportValidation.start(): ', inspect.stack()[1][1:4])
        # print('\nImportValidation.start_suite(): ')
        # print('Imported: ' + str(self.imported))
        pass

    def end_suite(self, suite, attrs):
        if self.imported.difference(self.used_imports):
            print('UNUSED IMPORTS: ')
        # print('ImportValidation.stop(): ', inspect.stack()[1][1:4])
            print(self.imported.difference(self.used_imports))

        self.used_imports = set()
        self.imported = set()

    def start_keyword(self, kw, attrs):
        # print('\nstart_keyword(' + str(attrs['libname']) + ')\n')
        self._add_used_method(attrs['libname'])

    # @classmethod
    # def add_import(self, resource):
    #     print('ImportValidation.add_import(): ')
    #     # print('ImportValidation.add_import(): ', inspect.stack()[1][1:4])
    #     ImportValidator.imported.add(resource)

    def _add_used_method(self, lib_name):
        # print('ImportValidation.add_used_method(): ')
        # print('ImportValidation.add_used_method(): ', inspect.stack()[1][1:4])
        self.used_imports.add(lib_name)

    def import_resource_or_library(self, name):
        # print('\nimport_resource_or_library(' + name + ')\n')
        self.imported.add(name)
        # print('import_resource_or_library: Imported: ' + str(self.imported))
