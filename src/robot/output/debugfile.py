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
import threading
import queue
from enum import Enum
import os
import asyncio

from robot.errors import DataError
from robot.utils import file_writer, seq2str2

from .logger import LOGGER
from .loggerapi import LoggerApi
from .loglevel import LogLevel


def DebugFile(path):
    if not path:
        LOGGER.info('No debug file')
        return None
    try:
        outfile = file_writer(path, usage='debug')
    except DataError as err:
        LOGGER.error(err.message)
        return None
    else:
        LOGGER.info('Debug file: %s' % path)
        return _DebugFileWriter(outfile)


def _worker_factory():
    _workers = {}
    while True:
        (outfile, q_res,) = _debug_worker._request_worker_q.get()
        if outfile not in _workers:
            _workers[outfile] = _debug_worker(outfile)
        q_res.put(_workers[outfile])


def _write_log2file_queue_endpoint(outfile, q):
    while True:
        elem_type, elem_data = q.get()
        if elem_type == _debug_worker._command.CLOSE:
            outfile.close()
            q.task_done()
            return
        elif elem_type == _debug_worker._command.WRITE:
            outfile.write(elem_data)
            outfile.flush()
            q.task_done()


class _debug_worker:
    def __init__(self, outfile):
        self._name = outfile.name
        self._out_q = queue.Queue()
        self._worker_thread = threading.Thread(target=_write_log2file_queue_endpoint, args=(outfile, self._out_q), daemon=False)
        self._worker_thread.start()

    @property
    def closed(self):
        if self._worker_thread.is_alive():
            return False
        self._out_q.join()
        return True

    @property
    def name(self):
        # safe as name is imutable
        return self._name

    class _command(Enum):
        CLOSE = 1
        WRITE = 2

    def close(self):
        self._out_q.put((_debug_worker._command.CLOSE, False,))

    def write(self, text):
        self._out_q.put((_debug_worker._command.WRITE, text,))

    _request_worker_q = queue.Queue()
    _t = threading.Thread(target=_worker_factory, daemon=True)


def _get_worker(outfile):
    q = queue.Queue()
    _debug_worker._request_worker_q.put((outfile, q,))
    return q.get()


def _get_thread_local_instance_DebugFileWriter(self):
    ct = threading.current_thread()
    if not hasattr(ct, "_DebugFileWriter"):
        ct._DebugFileWriter = _DebugFileWriter(self._orig_outfile)
    return ct._DebugFileWriter


class _DebugFileWriter(LoggerApi):
    _separators = {'SUITE': '=', 'TEST': '-', 'KEYWORD': '~'}
    multithread_capable = True

    def __init__(self, outfile):
        self._indent = 0
        self._kw_level = 0
        self._separator_written_last = False
        self._orig_outfile = outfile
        self._outfile = _get_worker(outfile)
        self._is_logged = LogLevel('DEBUG').is_logged

    def start_suite(self, data, result):
        self = _get_thread_local_instance_DebugFileWriter(self)
        self._separator('SUITE')
        self._start('SUITE', data.full_name, result.start_time)
        self._separator('SUITE')

    def end_suite(self, data, result):
        self = _get_thread_local_instance_DebugFileWriter(self)
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

    def close(self):
        self = _get_thread_local_instance_DebugFileWriter(self)
        if not self._outfile.closed:
            self._outfile.close()

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

    def _write(self, text, separator=False):
        self = _get_thread_local_instance_DebugFileWriter(self)
        if separator and self._separator_written_last:
            return
        inEventLoop = "regular"
        try:
            asyncio.get_running_loop()
            inEventLoop = "async"
        except RuntimeError:
            pass
        text = "".join(f"{os.getpgid()}\n{threading.current_thread().name}\t{inEventLoop}\t{item}\n" for item in text.rstrip().split('\n'))
        self._outfile.write(text)
        self._separator_written_last = separator


_debug_worker._t.start()
