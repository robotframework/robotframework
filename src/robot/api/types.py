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

"""Types that libraries and other extensions can utilize.

- The :class:`~robot.utils.secret.Secret` class is used for encapsulating
  passwords, tokens and other such secret information.

- :class:`KeywordName` and :class:`KeywordArguments` are used in type hints
  with keywords executing other keywords. External tools can recognize special
  arguments using these types and handle them adequately.

New in Robot Framework 7.4.
"""

from robot.utils.secret import Secret as Secret


class KeywordName(str):
    """Name of a keyword executed by another keyword."""


class KeywordArgument:
    """Argument of a keyword executed by another keyword."""
