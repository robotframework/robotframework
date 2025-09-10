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


# FIXME: Consider moving this to robot.api
class Secret:
    """Represent a secret value that should not be logged or displayed in plain text.

    This class is used to encapsulate sensitive information, such as passwords or
    API keys, ensuring that when the value is logged, it is not exposed by
    Robot Framework by its original value. Please note when libraries or
    tools use this class, they should ensure that the value is not logged
    or displayed in any way that could compromise its confidentiality. In some
    cases, this is not fully possible, example selenium or Playwright might
    still reveal the value in log messages or other outputs.

    Libraries or tools using the Secret class can use the value attribute to
    access the actual secret value when necessary.
    """

    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return f"{type(self).__name__}(value=<secret>)"

    def __repr__(self):
        return str(self)
