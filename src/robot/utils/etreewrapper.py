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

import sys


_ERROR = 'No valid ElementTree XML parser module found'


if sys.platform == 'cli':
    # Cannot use standard ET available on IronPython 2.7.0 or 2.7.1 because
    # it is broken:
    # http://ironpython.codeplex.com/workitem/31923
    # http://ironpython.codeplex.com/workitem/21407
    try:
        from elementtree import ElementTree as ET
    except ImportError:
        raise ImportError(_ERROR)

else:

    try:
        from xml.etree import cElementTree as ET
    except ImportError:
        try:
            import cElementTree as ET
        except ImportError:
            try:
                from xml.etree import ElementTree as ET
            except ImportError:
                try:
                    from elementtree import ElementTree as ET
                except ImportError:
                    raise ImportError(_ERROR)

