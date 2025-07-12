import sys
from os.path import abspath, dirname, join, normpath

curdir = dirname(abspath(__file__))
src = normpath(join(curdir, "..", "..", "..", "..", "..", "src"))
sys.path.insert(0, src)

from robot.utils import CONSOLE_ENCODING, SYSTEM_ENCODING  # noqa: E402

config = dict(arg.split(":") for arg in sys.argv[1:])
stdout = config.get("stdout", "hyv\xe4")
stderr = config.get("stderr", stdout)
encoding = config.get("encoding", "ASCII")
encoding = {
    "CONSOLE": CONSOLE_ENCODING,
    "SYSTEM": SYSTEM_ENCODING,
}.get(encoding, encoding)


sys.stdout.buffer.write(stdout.encode(encoding))
sys.stderr.buffer.write(stderr.encode(encoding))
