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

from robot.errors import DataError
from robot.result import Keyword as KeywordResult
from robot.variables import VariableAssignment

from .arguments import EmbeddedArguments
from .keywordimplementation import KeywordImplementation
from .model import Keyword as KeywordData
from .statusreporter import StatusReporter


class InvalidKeyword(KeywordImplementation):
    """Represents an invalid keyword call.

    Keyword may not have been found, there could have been multiple matches,
    or the keyword call itself could have been invalid.
    """

    type = KeywordImplementation.INVALID_KEYWORD

    def _get_embedded(self, name) -> "EmbeddedArguments|None":
        try:
            return super()._get_embedded(name)
        except DataError:
            return None

    def create_runner(self, name, languages=None):
        return InvalidKeywordRunner(self, name)

    def bind(self, data: KeywordData) -> "InvalidKeyword":
        return self.copy(parent=data.parent)


class InvalidKeywordRunner:

    def __init__(self, keyword: InvalidKeyword, name: "str|None" = None):
        self.keyword = keyword
        self.name = name or keyword.name
        if not keyword.error:
            raise ValueError("Executed 'InvalidKeyword' instance requires 'error'.")

    def run(self, data: KeywordData, result: KeywordResult, context, run=True):
        kw = self.keyword.bind(data)
        args = tuple(data.args)
        if data.named_args:
            args += tuple(f"{n}={v}" for n, v in data.named_args.items())
        result.config(
            name=self.name,
            owner=kw.owner.name if kw.owner else None,
            args=args,
            assign=tuple(VariableAssignment(data.assign)),
            type=data.type,
        )
        with StatusReporter(data, result, context, run, implementation=kw):
            # 'error' is can be set to 'None' by a listener that handles it.
            if run and kw.error is not None:
                raise DataError(kw.error)

    dry_run = run
