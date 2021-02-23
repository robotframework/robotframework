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

from functools import partial

from robot.errors import VariableError
from robot.utils import is_dict_like, is_list_like, normalize, RecommendationFinder


def variable_not_found(name, candidates, message=None, deco_braces=True):
    """Raise DataError for missing variable name.

    Return recommendations for similar variable names if any are found.
    """
    candidates = _decorate_candidates(name[0], candidates, deco_braces)
    normalizer = partial(normalize, ignore='$@&%{}_')
    message = RecommendationFinder(normalizer).find_and_format(
        name, candidates,
        message=message or "Variable '%s' not found." % name
    )
    raise VariableError(message)


def _decorate_candidates(identifier, candidates, deco_braces=True):
    template = '%s{%s}' if deco_braces else '%s%s'
    is_included = {'$': lambda value: True,
                   '@': is_list_like,
                   '&': is_dict_like,
                   '%': lambda value: True}[identifier]
    return [template % (identifier, name)
            for name in candidates if is_included(candidates[name])]
