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

import json
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import TextIO

from robot.version import get_full_version


class JsonLogger:

    def __init__(self, file: TextIO, rpa: bool = False):
        self.writer = JsonWriter(file)
        self.writer.start_dict(
            generator=get_full_version("Robot"),
            generated=datetime.now().isoformat(),
            rpa=Raw(self.writer.encode(rpa)),
        )
        self.containers = []

    def start_suite(self, suite):
        if not self.containers:
            name = "suite"
            container = None
        else:
            name = None
            container = "suites"
        self._start(container, name, id=suite.id)

    def end_suite(self, suite):
        self._end(
            name=suite.name,
            doc=suite.doc,
            metadata=suite.metadata,
            source=suite.source,
            rpa=suite.rpa,
            **self._status(suite),
        )

    def start_test(self, test):
        self._start("tests", id=test.id)

    def end_test(self, test):
        self._end(
            name=test.name,
            doc=test.doc,
            tags=test.tags,
            lineno=test.lineno,
            timeout=str(test.timeout) if test.timeout else None,
            **self._status(test),
        )

    def start_keyword(self, kw):
        if kw.type in ("SETUP", "TEARDOWN"):
            self._end_container()
            name = kw.type.lower()
            container = None
        else:
            name = None
            container = "body"
        self._start(container, name)

    def end_keyword(self, kw):
        self._end(
            name=kw.name,
            owner=kw.owner,
            source_name=kw.source_name,
            args=[str(a) for a in kw.args],
            assign=kw.assign,
            tags=kw.tags,
            doc=kw.doc,
            timeout=str(kw.timeout) if kw.timeout else None,
            **self._status(kw),
        )

    def start_for(self, item):
        self._start(type=item.type)

    def end_for(self, item):
        self._end(
            flavor=item.flavor,
            start=item.start,
            mode=item.mode,
            fill=UnlessNone(item.fill),
            assign=item.assign,
            values=item.values,
            **self._status(item),
        )

    def start_for_iteration(self, item):
        self._start(type=item.type)

    def end_for_iteration(self, item):
        self._end(assign=item.assign, **self._status(item))

    def start_while(self, item):
        self._start(type=item.type)

    def end_while(self, item):
        self._end(
            condition=item.condition,
            limit=item.limit,
            on_limit=item.on_limit,
            on_limit_message=item.on_limit_message,
            **self._status(item),
        )

    def start_while_iteration(self, item):
        self._start(type=item.type)

    def end_while_iteration(self, item):
        self._end(**self._status(item))

    def start_if(self, item):
        self._start(type=item.type)

    def end_if(self, item):
        self._end(**self._status(item))

    def start_if_branch(self, item):
        self._start(type=item.type)

    def end_if_branch(self, item):
        self._end(condition=item.condition, **self._status(item))

    def start_try(self, item):
        self._start(type=item.type)

    def end_try(self, item):
        self._end(**self._status(item))

    def start_try_branch(self, item):
        self._start(type=item.type)

    def end_try_branch(self, item):
        self._end(
            patterns=item.patterns,
            pattern_type=item.pattern_type,
            assign=item.assign,
            **self._status(item),
        )

    def start_group(self, item):
        self._start(type=item.type)

    def end_group(self, item):
        self._end(name=item.name, **self._status(item))

    def start_var(self, item):
        self._start(type=item.type)

    def end_var(self, item):
        self._end(
            name=item.name,
            scope=item.scope,
            separator=UnlessNone(item.separator),
            value=item.value,
            **self._status(item),
        )

    def start_return(self, item):
        self._start(type=item.type)

    def end_return(self, item):
        self._end(values=item.values, **self._status(item))

    def start_continue(self, item):
        self._start(type=item.type)

    def end_continue(self, item):
        self._end(**self._status(item))

    def start_break(self, item):
        self._start(type=item.type)

    def end_break(self, item):
        self._end(**self._status(item))

    def start_error(self, item):
        self._start(type=item.type)

    def end_error(self, item):
        self._end(values=item.values, **self._status(item))

    def message(self, msg):
        self._dict(**msg.to_dict())

    def errors(self, messages):
        self._list("errors", [m.to_dict(include_type=False) for m in messages])

    def statistics(self, stats):
        data = stats.to_dict()
        self._start(None, "statistics")
        self._dict(None, "total", **data["total"])
        self._list("suites", data["suites"])
        self._list("tags", data["tags"])
        self._end()

    def close(self):
        self.writer.end_dict()
        self.writer.close()

    def _status(self, item):
        return {
            "status": item.status,
            "message": item.message,
            "start_time": item.start_time.isoformat() if item.start_time else None,
            "elapsed_time": Raw(format(item.elapsed_time.total_seconds(), "f")),
        }

    def _dict(
        self,
        container: "str|None" = "body",
        name: "str|None" = None,
        /,
        **items,
    ):
        self._start(container, name, **items)
        self._end()

    def _list(self, name: "str|None", items: list):
        self.writer.start_list(name)
        for item in items:
            self._dict(None, None, **item)
        self.writer.end_list()

    def _start(
        self,
        container: "str|None" = "body",
        name: "str|None" = None,
        /,
        **items,
    ):
        if container:
            self._start_container(container)
        self.writer.start_dict(name, **items)
        self.containers.append(None)

    def _start_container(self, container):
        if self.containers[-1] != container:
            if self.containers[-1]:
                self.writer.end_list()
            self.writer.start_list(container)
            self.containers[-1] = container

    def _end(self, **items):
        self._end_container()
        self.containers.pop()
        self.writer.end_dict(**items)

    def _end_container(self):
        if self.containers[-1]:
            self.writer.end_list()
            self.containers[-1] = None


class JsonWriter:

    def __init__(self, file):
        self.encode = json.JSONEncoder(
            check_circular=False,
            separators=(",", ":"),
            default=self._handle_custom,
        ).encode
        self.file = file
        self.comma = False

    def _handle_custom(self, value):
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, Mapping):
            return dict(value)
        if isinstance(value, Sequence):
            return list(value)
        raise TypeError(type(value).__name__)

    def start_dict(self, name=None, /, **items):
        self._start(name, "{")
        self.items(**items)

    def _start(self, name, char):
        self._newline(newline=name is not None)
        self._name(name)
        self._write(char)
        self.comma = False

    def _newline(self, comma: "bool|None" = None, newline: bool = True):
        if self.comma if comma is None else comma:
            self._write(",")
        if newline:
            self._write("\n")

    def _name(self, name):
        if name:
            self._write(f'"{name}":')

    def _write(self, text):
        self.file.write(text)

    def end_dict(self, **items):
        self.items(**items)
        self._end("}")

    def _end(self, char, newline=True):
        self._newline(comma=False, newline=newline)
        self._write(char)
        self.comma = True

    def start_list(self, name=None, /):
        self._start(name, "[")

    def end_list(self):
        self._end("]", newline=False)

    def items(self, **items):
        for name, value in items.items():
            self._item(value, name)

    def _item(self, value, name=None):
        if isinstance(value, UnlessNone) and value:
            value = value.value
        elif not (value or value == 0 and not isinstance(value, bool)):
            return
        if isinstance(value, Raw):
            value = value.value
        else:
            value = self.encode(value)
        self._newline()
        self._name(name)
        self._write(value)
        self.comma = True

    def close(self):
        self._write("\n")
        self.file.close()


class Raw:

    def __init__(self, value):
        self.value = value


class UnlessNone:

    def __init__(self, value):
        self.value = value

    def __bool__(self):
        return self.value is not None
