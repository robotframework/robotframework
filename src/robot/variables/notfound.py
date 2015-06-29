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

from robot.errors import VariableError
from robot.utils import (is_dict_like, is_list_like, normalize,
                         RecommendationFinder)


def variable_not_found(name, candidates, msg=None, deco_braces=True):
    """Raise DataError for missing variable name.

    Return recommendations for similar variable names if any are found.
    """
    if msg is None:
        msg = "Variable '%s' not found." % name
    candidates = _decorate_candidates(name[0], candidates, deco_braces)
    normalizer = partial(normalize, ignore='$@%&*{}_', caseless=True,
                         spaceless=True)
    finder = RecommendationFinder(normalizer)
    recommendations = finder.find_recommendations(name, candidates)
    msg = finder.format_recommendations(msg, recommendations)
    raise VariableError(msg)


def _decorate_candidates(identifier, candidates, deco_braces=True):
    template = '%s{%s}' if deco_braces else '%s%s'
    is_included = {'$': lambda value: True,
                   '@': is_list_like,
                   '&': is_dict_like,
                   '%': lambda value: True}[identifier]
    return [template % (identifier, name)
            for name in candidates if is_included(candidates[name])]
