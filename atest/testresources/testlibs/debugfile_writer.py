from robot.api import logger
import multiprocessing
import threading
import robot.output.debugfile
import robot.output.logger


def _write_to_debugfile_p(q, name):
    robot.output.logger.LOGGER.register_logger(robot.output.debugfile._DebugFileWriterForChildProcessOrInterpreter(q, name))
    robot.output.logger.LOGGER.debug('Writing to debugfile from process')


def write_to_debugfile_from_thread():
    def write_to_debugfile():
        logger.debug('Writing to debugfile from thread')
    t = threading.Thread(target=write_to_debugfile, name="wr_thread")
    t.start()
    t.join()


def write_to_debugfile_from_process():
    for item in robot.output.logger.LOGGER:
        try:
            p = multiprocessing.Process(target=_write_to_debugfile_p, args=(item._q, item._name), name="wr_process")
            p.start()
            p.join()
            return
        except AttributeError:
            pass


async def write_to_debugfile_from_async():
    logger.debug('Writing to debugfile from async')

