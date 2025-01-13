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
import multiprocessing as mp
import threading
import asyncio
import io
import os
from enum import Enum
import collections
import base64

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
    try:
        if isinstance(path, Path):
            return _DebugFileWriterForFile(path, path.name)
        elif isinstance(path, io.TextIOWrapper):
            return _DebugFileWriterForStream(path)
        else:
            assert False, "unsupported debug output type"
    except Exception as e:
        LOGGER.error(f"Opening debug file '{str(path)}' failed: {get_error_message()}")
        raise e
        return None


def _write_log2file_queue_endpoint(q2log, qStatus):
    try:
        with io.open(q2log.get(), 'w', encoding='UTF-8', newline=None) as of:
            qStatus.put(None)
            while True:
                payload = q2log.get()
                if isinstance(payload, str):
                    of.write(payload)
                    of.flush()
                elif payload is None:
                    break
                else:
                    assert False, f"Unsupported payload type: {type(payload)} of value {payload}"

    except Exception as _:
        qStatus.put(f"Opening '{str(oPath)}' failed: {get_error_message()}")


def _get_thread_local_instance_DebugFileWriter(self):
    ct = threading.current_thread()
    async_id = self._get_async_id()
    if not hasattr(ct, "_DebugFileWriter"):
        ct._DebugFileWriter = {}
    if not async_id in ct._DebugFileWriter:
        if isinstance(self, _DebugFileWriterQueueBased):
            ct._DebugFileWriter[async_id] = _DebugFileWriterQueueBased(self._q, self._name)
        else:
            ct._DebugFileWriter[async_id] = self
    return ct._DebugFileWriter[async_id]


class _DebugFileWriter(LoggerApi):
    _separators = {'SUITE': '=', 'TEST': '-', 'KEYWORD': '~'}

    def __init__(self, outfile, name):
        self._indent = 0
        self._kw_level = 0
        self._separator_written_last = False
        self._orig_outfile = outfile
        self._is_logged = LogLevel('DEBUG').is_logged
        self._name = name

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
            LOGGER.debug_file(Path(self._name))
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
    
    def _get_async_id(self):
         try:
            loop_id = id(asyncio.get_running_loop())
            loop_id_bytes = loop_id.to_bytes((loop_id.bit_length() + 7) // 8, byteorder="big")
            return f"""async_{base64.b64encode(loop_id_bytes).decode("utf-8")}"""
         except RuntimeError:
            return "std_thread"

    def _prepare_text(self, text):
        inEventLoop = self._get_async_id()
        return "".join(f"{mp.current_process().name}\t{threading.current_thread().name}\t{inEventLoop}\t{item}\n" for item in text.rstrip().split('\n'))

class _DebugFileWriterQueueBased(_DebugFileWriter):
    def __init__(self, q, name):
        super().__init__(None, name)
        self._q = q

    def close(self):
        self = _get_thread_local_instance_DebugFileWriter(self)
        self._q.put(None, timeout=None)

    def _write(self, text, separator=False):
        self = _get_thread_local_instance_DebugFileWriter(self)
        text = self._prepare_text(text)
        self._q.put(text, timeout=None)
        self._separator_written_last = separator


class _DebugFileWriterForStream(_DebugFileWriter):
    _separators = {'SUITE': '=', 'TEST': '-', 'KEYWORD': '~'}
    multithread_capable = False

    def __init__(self, outfile):
        super().__init__(outfile, outfile.name)
        self._outfile = outfile

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


class _DebugFileWriterForFile(_DebugFileWriterQueueBased):
    multithread_capable = True

    def __init__(self, outfile, name):
        super().__init__(outfile, name)
        self._q = mp.Queue()
        _qStatus = mp.Queue()
        mp.Process(target=_write_log2file_queue_endpoint, args=(self._q, _qStatus,), daemon=True).start()
        self._q.put(outfile)
        try:
            if payload := _qStatus.get(timeout=None) is not None:
                raise DataError(payload)
        except Exception as e:
            raise e
        finally:
            _qStatus.close()
            _qStatus.join_thread()
