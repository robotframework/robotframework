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


LEVELS = {
  "NONE"  : 100, 
  "ERROR" : 60,
  "FAIL"  : 50,
  "WARN"  : 40,
  "INFO"  : 30,
  "DEBUG" : 20,
  "TRACE" : 10,
}


def get_level(string):
    try:
        return LEVELS[string.upper()]
    except KeyError:
        raise DataError("Invalid log level '%s'" % string)
    
def _get_levels_as_string(level_dict):
    level_tuples = level_dict.items()
    level_tuples.sort(lambda t1, t2: cmp(t1[1], t2[1]))
    levels = [ t[0] for t in level_tuples ]
    return utils.seq2str(levels)
    

LEVELS_AS_STRING = _get_levels_as_string(LEVELS)
