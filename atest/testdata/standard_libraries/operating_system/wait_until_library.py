import os
from threading import Timer


class wait_until_library:

    def __init__(self):
        self._timers = []

    def remove_after_sleeping(self, *paths):
        for p in paths:
            remover = os.rmdir if os.path.isdir(p) else os.remove
            self._run_after_sleeping(remover, p)

    def create_after_sleeping(self, path, directory=False):
        if directory:
            self._run_after_sleeping(os.mkdir, path)
        else:
            self._run_after_sleeping(lambda: open(path, "w", encoding="ASCII").close())

    def _run_after_sleeping(self, method, *args):
        self._timers.append(Timer(0.1, method, args))
        self._timers[-1].start()
