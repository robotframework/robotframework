from robot.api import logger
import multiprocessing
import threading
import robot.output.debugfile
import robot.output.logger
import sys


# On windows and mac fork is not an option and for multiprocessing a new process needs to be spawned.
#
# On Mac this is due to the use of threads which is incompatible to the usage of fork.
# On Windows it is the lack of the existance of fork
#
# This is a technology proof of concept how this can be solved, over the short term the logger needs
# to be replaced with a properly used one, if this is to be considered as an option, a 
def _write_to_debugfile_p(q, name):
    robot.output.logger.LOGGER.register_logger(robot.output.debugfile._DebugFileWriterForChildProcessOrInterpreter(q, name))
    sys.modules["logger"] = robot.output.logger.LOGGER
    import logger

    # Starting from here there is a very reduced robotframework logger available...
    logger.debug('Writing to debugfile from process')

def write_to_debugfile_from_process():
    for item in robot.output.logger.LOGGER:
        try:
            p = multiprocessing.Process(target=_write_to_debugfile_p, args=(item._q, item._name), name="wr_process")
            p.start()
            p.join()
            return
        except AttributeError:
            pass

def write_to_debugfile_from_thread():
    def write_to_debugfile():
        logger.debug('Writing to debugfile from thread')
    t = threading.Thread(target=write_to_debugfile, name="wr_thread")
    t.start()
    t.join()

async def write_to_debugfile_from_async():
    logger.debug('Writing to debugfile from async')

