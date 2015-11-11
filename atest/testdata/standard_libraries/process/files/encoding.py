from os.path import abspath, dirname, join, normpath
import sys

PY2 = sys.version_info[0] < 3
curdir = dirname(abspath(__file__))
src = normpath(join(curdir, '..', '..', '..', '..', '..', 'src'))
sys.path.insert(0, src)

from robot.utils.encoding import CONSOLE_ENCODING, SYSTEM_ENCODING


config = dict(arg.split(':') for arg in sys.argv[1:])
stdout = config.get('stdout', u'hyv\xe4')
stderr = config.get('stderr', stdout)
encoding = config.get('encoding', 'ASCII')
encoding = {'CONSOLE': CONSOLE_ENCODING,
            'SYSTEM': SYSTEM_ENCODING}.get(encoding, encoding)

if PY2 and isinstance(stdout, bytes):
    stdout = stdout.decode(SYSTEM_ENCODING)
if PY2 and isinstance(stderr, bytes):
    stderr = stderr.decode(SYSTEM_ENCODING)

(sys.stdout if PY2 else sys.stdout.buffer).write(stdout.encode(encoding))
(sys.stderr if PY2 else sys.stderr.buffer).write(stderr.encode(encoding))
