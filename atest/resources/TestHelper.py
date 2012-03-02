import os
import sys
from stat import S_IREAD, S_IWRITE


class TestHelper:

    def set_read_only(self, path):
        os.chmod(path, S_IREAD)

    def set_read_write(self, path):
        os.chmod(path, S_IREAD | S_IWRITE)

    def get_output_name(self, *datasources):
        if not datasources:
            raise RuntimeError('One or more data sources must be given!')
        if len(datasources) == 1:
            return self._get_name(datasources[0])
        return '_'.join(self._get_name(source) for source in datasources)

    def _get_name(self, path):
        return os.path.splitext(os.path.basename(path))[0]

    def running_on_jython(self, interpreter):
        return 'jython' in interpreter

    def running_on_python(self, interpreter):
        return not self.running_on_jython(interpreter)

    def running_on_linux(self):
        return 'linux' in sys.platform
