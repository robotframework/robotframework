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

from functools import partial

from robot.errors import DataError
from robot.utils import get_env_vars, normalize, RecommendationFinder


def raise_not_found(name, candidates, msg=None, env_vars=False):
    """Raise DataError for missing variable name.

    Return recommendations for similar variable names if any are found.
    """
    if msg is None:
        msg = "Variable '%s' not found." % name
    if env_vars:
        candidates += ['%%{%s}' % var for var in get_env_vars()]
    normalizer = partial(normalize, ignore='$@%&*{}_', caseless=True,
                         spaceless=True)
    finder = RecommendationFinder(normalizer)
    recommendations = finder.find_recommendations(name, candidates)
    msg = finder.format_recommendations(msg, recommendations)
    raise DataError(msg)
