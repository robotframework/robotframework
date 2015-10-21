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

"""Implementation of the public test library logging API.

This is exposed via :py:mod:`robot.api.logger`. Implementation must reside
here to avoid cyclic imports.
"""

import sys
import threading
import re
import multiprocessing

from robot.errors import DataError
from robot.utils import unic, encode_output

from .logger import LOGGER
from .loggerhelper import Message

MESSAGES = multiprocessing.Manager().dict()
M_LOCK = multiprocessing.Manager().RLock()
BACKGROUND_LOGGING = False
COUNT = 0

LOGGING_THREADS = ('MainThread', 'MainProcess', 'RobotFrameworkTimeoutThread')


def write(msg, level, html=False):
    # Callable messages allow lazy logging internally, but we don't want to
    # expose this functionality publicly. See the following issue for details:
    # https://github.com/robotframework/robotframework/issues/1505
    if callable(msg):
        msg = unic(msg)
    if level.upper() not in ('TRACE', 'DEBUG', 'INFO', 'HTML', 'WARN', 'ERROR'):
        raise DataError("Invalid log level '%s'." % level)
            
    with M_LOCK:
        thread  = threading.currentThread().getName()
        process = multiprocessing.current_process().name
        
        if thread not in LOGGING_THREADS: 
            name = thread
        elif process not in LOGGING_THREADS:
            name = process
        else:
            LOGGER.log_message(Message(msg, level, html))
            return    
  
        # Only log background messages if enabled. If disabled, empty any
        # stored messages
        if not BACKGROUND_LOGGING:
            return
        
        if name not in MESSAGES.keys():
            MESSAGES[name] = [[msg, level, html]]
        else:
            a = MESSAGES[name]
            a.append([msg, level, html])
            MESSAGES[name] = a


def trace(msg, html=False):
    write(msg, 'TRACE', html)


def debug(msg, html=False):
    write(msg, 'DEBUG', html)


def info(msg, html=False, also_console=False):
    write(msg, 'INFO', html)
    if also_console:
        console(msg)


def warn(msg, html=False):
    write(msg, 'WARN', html)


def error(msg, html=False):
    write(msg, 'ERROR', html)


def console(msg, newline=True, stream='stdout'):
    msg = unic(msg)
    if newline:
        msg += '\n'
    stream = sys.__stdout__ if stream.lower() != 'stderr' else sys.__stderr__
    stream.write(encode_output(msg))
    stream.flush()

    
def log_background_messages(name=None):
    """Forwards messages logged on background to Robot Framework log.

    By default forwards all messages logged by all threads, but can be
    limited to a certain thread by passing thread's name as an argument.
    This method must be called from the main thread.

    Logged messages are removed from the message storage.
    """
    global MESSAGES
    
    # This tries to implement some kind of ordering based thread/process name
    # to ensure that the buffered messages are written to the log in the
    # correct order. Generally it seems to work OK but it can be a
    # bit hit and miss with poolworkers (they're not always ordered correctly).
    convert  = lambda text: int(text) if text.isdigit() else text
    alphanum = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    
    thread  = threading.currentThread().getName()
    process = multiprocessing.current_process().name

    if thread not in LOGGING_THREADS and process not in LOGGING_THREADS:
        raise RuntimeError('Logging background messages is only allowed from '
                           'main thread. Current thread name: {},{}'.
                           format(thread, process))
        
    if not BACKGROUND_LOGGING:
        raise RuntimeError('Logging background messages is currently disabled')
    
    if name:
        if name not in MESSAGES.keys():
            raise KeyError('Process/thread name \'{}\' not found in background '
                           'logger dictionary'.format(name))
        
        for message in MESSAGES[name]:
            write(message[0], message[1], message[2])
            
        MESSAGES.pop(name, None)
        return
    
    for name in sorted(MESSAGES.keys(), key=alphanum):
        for message in MESSAGES[name]:
            write(message[0], message[1], message[2])
        MESSAGES.pop(name, None)
