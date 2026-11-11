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

# These types are exposed via `robot.api.types` and users should import them
# from there. They are implemented here to avoid recursive imports when they
# are needed by `robot.running.arguments.typeinfo`. `__module__` is set so that
# the types are still documented and shown as part of `robot.api.types`.


class KeywordName(str):
    """Name of a keyword executed by another keyword."""

    __module__ = "robot.api.types"


class KeywordArgument:
    """Argument of a keyword executed by another keyword."""

    __module__ = "robot.api.types"
