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

"""A library providing dialogs for interacting with users.

``Dialogs`` is Robot Framework's standard library that provides means
for pausing the test or task execution and getting input from users.

Long lines in the provided messages are wrapped automatically. If you want
to wrap lines manually, you can add newlines using the ``\\n`` character
sequence.

The library has a known limitation that it cannot be used with timeouts.
"""

from robot.version import get_version

import importlib
import multiprocessing as mp
import concurrent.futures
from functools import wraps


__version__ = get_version()
__all__ = ['execute_manual_step', 'get_value_from_user',
           'get_selection_from_user', 'pause_execution', 'get_selections_from_user']

_ctx = mp.get_context("spawn") # spawn is thread safe (forkserver would also work, but is not available on windows, fork is not thread safe)
_pool = concurrent.futures.ProcessPoolExecutor(max_workers=1, mp_context=_ctx) # only one worker, this makes calls sequential, eventhough parallel calls would be possible

def _process_worker(fun_name, args, kwargs):
    m = importlib.import_module("robot.libraries.dialogs_py") 
    # dialogs_py is only loaded in target process, 
    # tkinter is not loaded before the function is
    # executed.
    #
    # This avoids the problem of tkinter not beeing pickleable
    return getattr(m, fun_name)(*args, **kwargs)

def run_in_process(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        return _pool.submit(_process_worker, fun.__name__, args, kwargs).result()
    return wrapper

# the acutall functions are implemented here
_dialogs_py = importlib.import_module('robot.libraries.dialogs_py')


for name in __all__:
    globals()[name] = run_in_process(getattr(_dialogs_py, name))
