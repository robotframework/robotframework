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

from pathlib import Path
import multiprocessing
import threading
import asyncio
import io
import os
from enum import Enum

from robot.errors import DataError
from robot.utils.error import get_error_message
from robot.utils import file_writer, seq2str2

from .logger import LOGGER
from .loggerapi import LoggerApi
from .loglevel import LogLevel


def DebugFile(path):
    if not path:
        LOGGER.info('No debug file')
        return None

    LOGGER.info('Debug file: %s' % path)
    if isinstance(path, Path):
        return _DebugFileWriterForFile(path)
    elif isinstance(path, io.TextIOWrapper):
        return _DebugFileWriterForStream(path)
    else:
        assert False, "unsupported debug output type"


class _command(Enum):
    CLOSE = 1
    WRITE = 2
    START = 3


def _write_log2file_queue_endpoint(q2log, qStatus):
    targets = {}
    usage_count = {}
    while True:
        oPath, elem_type, elem_data = q2log.get()
        
        if elem_type == _command.START:
            if oPath not in usage_count:
                usage_count[oPath] = 0
            usage_count[oPath] += 1
            if oPath not in targets:
                try:
                    targets[oPath] = io.open(oPath, 'w', encoding='UTF-8', newline=None)
                except Exception as e:
                    pass
                    qStatus.put((oPath, DataError(f"Opening '{str(oPath)}' failed: {get_error_message()}"),))
                    q2log.task_done()
                    continue
            qStatus.put((oPath, "OK",))
        elif elem_type == _command.CLOSE:
            try:
                usage_count[oPath] -= 1
                if 0 == usage_count[oPath]:
                    targets[oPath].close()
            except Exception as e:
                pass
        elif elem_type == _command.WRITE:
            targets[oPath].write(elem_data)
            targets[oPath].flush()
        q2log.task_done()
        if sum(usage_count.values()) == 0:
            break

def _get_thread_local_instance_DebugFileWriter(self):
    ct = threading.current_thread()
    if not hasattr(ct, "_DebugFileWriter"):
        ct._DebugFileWriter = type(self)(self._orig_outfile)
    return ct._DebugFileWriter


class _DebugFileWriter(LoggerApi):
    _separators = {'SUITE': '=', 'TEST': '-', 'KEYWORD': '~'}

    def __init__(self, outfile):
        self._indent = 0
        self._kw_level = 0
        self._separator_written_last = False
        self._orig_outfile = outfile
        self._is_logged = LogLevel('DEBUG').is_logged
        ct = threading.current_thread()
        ct._DebugFileWriter = self

    def start_suite(self, data, result):
        self = _get_thread_local_instance_DebugFileWriter(self)
        self._separator('SUITE')
        self._start('SUITE', data.full_name, result.start_time)
        self._separator('SUITE')

    def end_suite(self, data, result):
        self._separator('SUITE')
        self._end('SUITE', data.full_name, result.end_time, result.elapsed_time)
        self._separator('SUITE')
        if self._indent == 0:
            LOGGER.debug_file(Path(self._outfile.name))
            self.close()

    def start_test(self, data, result):
        self = _get_thread_local_instance_DebugFileWriter(self)
        self._separator('TEST')
        self._start('TEST', result.name, result.start_time)
        self._separator('TEST')

    def end_test(self, data, result):
        self = _get_thread_local_instance_DebugFileWriter(self)
        self._separator('TEST')
        self._end('TEST', result.name, result.end_time, result.elapsed_time)
        self._separator('TEST')

    def start_keyword(self, data, result):
        self = _get_thread_local_instance_DebugFileWriter(self)
        if self._kw_level == 0:
            self._separator('KEYWORD')
        self._start(result.type, result.full_name, result.start_time, seq2str2(result.args))
        self._kw_level += 1

    def end_keyword(self, data, result):
        self = _get_thread_local_instance_DebugFileWriter(self)
        self._end(result.type, result.full_name, result.end_time, result.elapsed_time)
        self._kw_level -= 1

    def start_body_item(self, data, result):
        self = _get_thread_local_instance_DebugFileWriter(self)
        if self._kw_level == 0:
            self._separator('KEYWORD')
        self._start(result.type, result._log_name, result.start_time)
        self._kw_level += 1

    def end_body_item(self, data, result):
        self = _get_thread_local_instance_DebugFileWriter(self)
        self._end(result.type, result._log_name, result.end_time, result.elapsed_time)
        self._kw_level -= 1

    def log_message(self, msg):
        self = _get_thread_local_instance_DebugFileWriter(self)
        if self._is_logged(msg):
            self._write(f'{msg.timestamp} - {msg.level} - {msg.message}')

    def _start(self, type, name, timestamp, extra=''):
        self = _get_thread_local_instance_DebugFileWriter(self)
        if extra:
            extra = f' {extra}'
        indent = '-' * self._indent
        self._write(f'{timestamp} - INFO - +{indent} START {type}: {name}{extra}')
        self._indent += 1

    def _end(self, type, name, timestamp, elapsed):
        self = _get_thread_local_instance_DebugFileWriter(self)
        self._indent -= 1
        indent = '-' * self._indent
        elapsed = elapsed.total_seconds()
        self._write(f'{timestamp} - INFO - +{indent} END {type}: {name} ({elapsed} s)')

    def _separator(self, type_):
        self = _get_thread_local_instance_DebugFileWriter(self)
        self._write(self._separators[type_] * 78, separator=True)

    def _prepare_text(self, text):
        inEventLoop = "regular"
        try:
            asyncio.get_running_loop()
            inEventLoop = "async"
        except RuntimeError:
            pass
        return "".join(f"{multiprocessing.current_process().name}\t{threading.current_thread().name}\t{inEventLoop}\t{item}\n" for item in text.rstrip().split('\n'))


class _DebugFileWriterForStream(_DebugFileWriter):
    _separators = {'SUITE': '=', 'TEST': '-', 'KEYWORD': '~'}
    multithread_capable = False

    def __init__(self, outfile):
        super().__init__(outfile)
        self._outfile = outfile
        ct = threading.current_thread()
        ct._DebugFileWriter = self

    def close(self):
        self = _get_thread_local_instance_DebugFileWriter(self)
        if not self._outfile.closed:
            self._outfile.close()

    def _write(self, text, separator=False):
        self = _get_thread_local_instance_DebugFileWriter(self)
        if separator and self._separator_written_last:
            return
        text = self._prepare_text(text)
        self._outfile.write(text.rstrip() + '\n')
        self._outfile.flush()
        self._separator_written_last = separator


class _DebugFileWriterForFile(_DebugFileWriter):
    _q = multiprocessing.JoinableQueue()
    _qStatus = multiprocessing.Queue()
    _p = multiprocessing.Process(target=_write_log2file_queue_endpoint, args=(_q, _qStatus,))
    _p.daemon = True
    multithread_capable = True

    def __init__(self, outfile):
        self._indent = 0
        self._kw_level = 0
        self._separator_written_last = False
        self._orig_outfile = outfile
        self._outfile = outfile
        self._is_logged = LogLevel('DEBUG').is_logged
        
        _DebugFileWriterForFile._q.put((outfile, _command.START, None,))
        ct = threading.current_thread()
        ct._DebugFileWriter = self
        while True:
            (lPath, status) = _DebugFileWriterForFile._qStatus.get(timeout=5)
            if str(lPath) == str(outfile):
                if status != "OK":
                    raise status
                break
            else:
                _DebugFileWriterForFile._qStatus.put((lPath, status))

    def close(self):
        self = _get_thread_local_instance_DebugFileWriter(self)
        _DebugFileWriterForFile._q.put((self._orig_outfile, _command.CLOSE, None))
        _DebugFileWriterForFile._q.join()

    def _write(self, text, separator=False):
        self = _get_thread_local_instance_DebugFileWriter(self)
        text = self._prepare_text(text)
        _DebugFileWriterForFile._q.put((self._orig_outfile, _command.WRITE, text))
        self._separator_written_last = separator

if multiprocessing.current_process().name == 'MainProcess':
    _DebugFileWriterForFile._p.start()
