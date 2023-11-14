import asyncio

from robot.api import logger


class AsyncStop:

    async def async_test(self):
        logger.info("Start Sleep", also_console=True)
        await asyncio.sleep(2)
        logger.info("End Sleep", also_console=True)

    async def async_sleep(self, time: int):
        await asyncio.sleep(time)
