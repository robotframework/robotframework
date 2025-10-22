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


class Secret:
    """Encapsulates secrets to avoid them being shown in Robot Framework logs.

    The typical usage is using this class in `library keyword type hints`__ to
    indicate that only :class:`Secret` values are accepted. How to create these
    objects in the data and elsewhere is explained in the `User Guide`__.

    The encapsulated value is available in the :attr:`value` attribute, and it
    is mainly meant to be accessed by library keywords. Values are not hidden
    or encrypted, so they are available for all code that can access these
    objects directly or indirectly via Robot Framework APIs.

    The string representation of these objects does not disclose encapsulated
    values, so they are not visible in logs even if these objects themselves
    are logged. Notice, though, that if a keyword passes the actual value
    further, it may be logged or otherwise disclosed later.

    This class should be imported via the :mod:`robot.api.types` module.

    .. sourcecode:: python

       from robot.api.types import Secret


       def example(username: str, password: Secret):
           user = authenticate(username, password.value)
           ...

    New in Robot Framework 7.4.

    __ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#secret-type
    __ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#secret-variables
    """

    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return "<secret>"

    def __repr__(self):
        return f"{type(self).__name__}(value=<secret>)"
