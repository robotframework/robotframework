from robot.api import logger
import multiprocessing
import threading


def write_to_debugfile_from_thread():
    def write_to_debugfile():
        logger.debug('Writing to debugfile from thread')
    t = threading.Thread(target=write_to_debugfile, name="wr_thread")
    t.start()
    t.join()


def write_to_debugfile_from_process():
    def write_to_debugfile():
        logger.debug('Writing to debugfile from process')
    p = multiprocessing.Process(target=write_to_debugfile, name="wr_process")
    p.start()
    p.join()

async def write_to_debugfile_from_async():
    logger.debug('Writing to debugfile from async')

