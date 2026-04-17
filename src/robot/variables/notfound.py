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

from collections.abc import Mapping, Sequence
from functools import partial
from typing import NoReturn

from robot.errors import VariableError
from robot.utils import is_dict_like, is_list_like, normalize, RecommendationFinder


def variable_not_found(
    name: str,
    candidates: "Mapping[str, object]",
    message: "str | None" = None,
    deco_braces: bool = True,
) -> NoReturn:
    """Raise `VariableError` for missing variable name.

    Error message includes recommendations for similar variable names if any are
    found. Finding recommendations has a performance effect, so this function
    should only been called when such information is actually useful.
    """
    recommender = RecommendationFinder(normalizer=partial(normalize, ignore="$@&%{}_"))
    recommendations = _decorate_recommendations(
        name[0],
        recommender.find(name, candidates),
        candidates,
        deco_braces,
    )
    message = recommender.format(
        message or f"Variable '{name}' not found.",
        recommendations,
    )
    raise VariableError(message)


def _decorate_recommendations(
    identifier: str,
    recommendations: "Sequence[str]",
    candidates: "Mapping[str, object]",
    deco_braces: bool = True,
) -> "list[str]":
    template = "%s{%s}" if deco_braces else "%s%s"
    is_included = {
        "$": lambda value: True,
        "@": is_list_like,
        "&": is_dict_like,
        "%": lambda value: True,
    }[identifier]
    return [
        template % (identifier, name)
        for name in recommendations
        if is_included(candidates[name])
    ]
