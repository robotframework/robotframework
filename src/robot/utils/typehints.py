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

from typing import Any, Callable, TypeVar

T = TypeVar("T", bound=Callable[..., Any])

# Type Alias for objects that are only known at runtime. This should be Used as a
# default value for generic classes that also use `@copy_signature` decorator
KnownAtRuntime = type(object)


def copy_signature(target: T) -> Callable[..., T]:
    """A decorator that applies the signature of `T` to any function that it decorates
    see https://github.com/python/typing/issues/270#issuecomment-555966301 for source
    and discussion.
    """

    def decorator(func):
        return func

    return decorator
