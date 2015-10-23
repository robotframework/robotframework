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

"""Package hosting Robot Framework standard test libraries.

Libraries are mainly used externally in the test data, but they can be
also used by custom test libraries if there is a need. Especially
the :class:`~robot.libraries.BuiltIn.BuiltIn` library is often useful
when there is a need to interact with the framework.

Because libraries are documented using Robot Framework's own documentation
syntax, the generated API docs are not that well formed. It is thus better
to find the generated library documentations, for example, via
the http://robotframework.org web site.
"""

STDLIBS = frozenset(('BuiltIn', 'Collections', 'DateTime', 'Dialogs', 'Easter',
                     'OperatingSystem', 'Process', 'Remote', 'Reserved',
                     'Screenshot', 'String', 'Telnet', 'XML'))
