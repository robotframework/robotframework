from typing import Any, Sequence
import robot.api.logger
from enum import Enum
from dataclasses import dataclass
import queue
from functools import wraps
import robot.errors
import multiprocessing as mp
import importlib


class responses(Enum):
    SUCCESS = 1
    EXCEPTION = 2
    LOG = 3

@dataclass
class _subprocess_call:
    name: str
    args: Sequence
    kwargs: dict


@dataclass
class _subprocess_response:
    response_type: responses
    value: Any


def _process_worker_for_decorator(libnameIn, classname,  qToSubprocess, qFromSubprocess):
    infra = importlib.import_module("robot.api.deco")
    infra.run_in_its_own_process_decorator._trunk = False
    logger = importlib.import_module("robot.api.logger")

    for logfunction in ["trace", "debug", "console", "info", "warn", "error", "write"]:
        def _worker(*args, **kwargs):
            qFromSubprocess.put(_subprocess_response(response_type=responses.LOG, value=(logfunction, args, kwargs)))
        setattr(logger, logfunction, _worker)

    m = importlib.import_module(libnameIn)
    if classname:
        m = getattr(m, classname)
    while True:
        try:
            call = qToSubprocess.get()
            result = getattr(m, call.name)(*call.args, **call.kwargs)
            qFromSubprocess.put(_subprocess_response(response_type=responses.SUCCESS, value=result))
        except Exception as e:
            qFromSubprocess.put(_subprocess_response(response_type=responses.EXCEPTION, value=e))


class run_in_its_own_process_decorator:
    _trunk = True
    def __init__(self, module_name, class_name=None, ctx="spawn"):
        self._module_name = module_name
        self._class_name = class_name
        if self._trunk:
            self._ctx = mp.get_context(ctx)
            self._setup()

    def _setup(self):
        self._qToSubprocess = self._ctx.Queue()
        self._qFromSubprocess = self._ctx.Queue()
        self._process = self._ctx.Process(target=_process_worker_for_decorator,
                                        args=(self._module_name, self._class_name, self._qToSubprocess, self._qFromSubprocess),
                                        daemon=True)
        self._process.start()

    def __call__(self, fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            if self._trunk:
                assert self._process.is_alive(), "Subprocess has died"
                self._qToSubprocess.put(_subprocess_call(fun.__name__, args, kwargs))
                while True:
                    try:
                        response = self._qFromSubprocess.get(timeout=0.010)
                        if response.response_type ==  responses.SUCCESS:
                            return response.value
                        elif response.response_type == responses.EXCEPTION:
                            raise response.value
                        elif response.response_type == responses.LOG:
                            (method, args, kwargs,) = response.value
                            getattr(robot.api.logger, method)(*args, **kwargs)
                            print((method, args, kwargs,))
                        else:
                            assert False, "Unknown response type"
                    except queue.Empty:
                        pass
                    except robot.errors.TimeoutError:
                        self._process.terminate()
                        self._process.join()
                        self._qToSubprocess.close()
                        self._qFromSubprocess.close()
                        self._setup()
                        raise
            else:
                return fun(*args, **kwargs)
        return wrapper