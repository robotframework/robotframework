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

import os
from os.path import abspath, dirname, join, normpath
import importlib.resources
import pathlib
import sys
import logging

# class HtmlTemplate:
#     def __init__(self, filename):
#         logging.error("---------------------")
#         logging.error(filename)
#         parts = pathlib.Path(filename).parts
#         resource_name = parts[-1]
#         parts = list(parts[:-1])
#         idx = len(parts) - 1
#         #logging.error(parts)
#         idx = 0
#         while idx < (len(parts)):
#             if parts[idx] == ".." and len(parts)>idx:
#                 del parts[idx]
#                 del parts[idx-1]
#                 logging.error(parts)
#                 logging.error(idx)
#             idx+=1

#         parts = (item.replace(".", "") for item in parts)

#         modulepart = "robot.htmldata." + ".".join(parts)
#         logging.error(modulepart +": " + resource_name)

#         self._data = importlib.resources.open_text(modulepart, resource_name).read().split()
#         #logging.error(self._data)

#     def __iter__(self):
#         for line in self._data:
#             yield line.rstrip()


#def HtmlTemplate(filename):
#    importlib.resources.open_text("robot.htmldata", "common.css")



class HtmlTemplate:
    _base_dir = join(dirname(abspath(__file__)), '..', 'htmldata')

    def __init__(self, filename):
        self._path = normpath(join(self._base_dir, filename.replace('/', os.sep)))
        logging.error("---------------------")
        logging.error(filename)
        parts = pathlib.Path(filename).parts
        resource_name = parts[-1]
        parts = list(parts[:-1])
        idx = len(parts) - 1
        #logging.error(parts)
        idx = 0
        while idx < (len(parts)):
            if parts[idx] == ".." and len(parts)>idx:
                del parts[idx]
                del parts[idx-1]
                logging.error(parts)
                logging.error(idx)
            idx+=1

        parts = (item.replace(".", "") for item in parts)

        modulepart = "robot.htmldata." + ".".join(parts)
        logging.error(modulepart +": " + resource_name)

        self._data = importlib.resources.open_text(modulepart, resource_name)
#         #logging.error(self._data)

    def __iter__(self):
        for line in self._data:
            yield line