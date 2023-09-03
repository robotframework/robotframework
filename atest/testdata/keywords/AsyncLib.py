import asyncio

from robot.libraries.BuiltIn import BuiltIn


class Hanger:

    def __init__(self) -> None:
        self.task = None
        self.ticks = []

    async def start_async_process(self):
        while True:
            self.ticks.append('tick')
            await asyncio.sleep(0.01)


class AsyncLib:

    async def basic_async_test(self):
        await asyncio.sleep(0.1)
        return 'Got it'

    def async_with_run_inside(self):
        async def inner():
            await asyncio.sleep(0.1)
            return 'Works'
        return asyncio.run(inner())

    async def can_use_gather(self):
        tasks = [asyncio.sleep(0.1) for _ in range(5)]
        await asyncio.gather(*tasks)

    async def create_hanger(self):
        hanger = Hanger()
        hanger.task = asyncio.create_task(hanger.start_async_process())
        return hanger

    async def stop_task_from_hanger(self, hanger):
        hanger.task.cancel()

    async def run_keyword_using_builtin(self):
        return await BuiltIn().run_keyword("Basic Async Test")

    async def create_task_with_loop(self):
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.basic_async_test())
        return await task
