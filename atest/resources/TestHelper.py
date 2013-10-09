import os
import sys
from stat import S_IREAD, S_IWRITE

from robot.api import logger


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

    def file_should_have_correct_line_separators(self, output, sep=os.linesep):
        if os.path.isfile(output):
            with open(output, 'rb') as infile:
                output = infile.read().decode('UTF-8')
        if sep not in output:
            self._wrong_separators('Output has no %r separators' % sep, output)
        extra_r = output.replace(sep, '').count('\r')
        extra_n = output.replace(sep, '').count('\n')
        if extra_r or extra_n:
            self._wrong_separators("Output has %d extra \\r and %d extra \\n"
                                   % (extra_r, extra_n), output)

    def _wrong_separators(self, message, output):
        logger.info(repr(output).replace('\\n', '\\n\n'))
        failure = AssertionError(message)
        failure.ROBOT_CONTINUE_ON_FAILURE = True
        raise failure
