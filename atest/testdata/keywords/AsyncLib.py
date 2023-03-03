import asyncio

class Hanger:

    def __init__(self) -> None:
        self.task = None
        self.ticks = []
    
    async def start_async_process(self):
        while True:
            self.ticks.append('tick')
            await asyncio.sleep(2)

class AsyncLib:

    def __init__(self) -> None:
        pass

    async def basic_async_test(self):
        await asyncio.sleep(2)
        return 'Got it'

    def async_with_run_inside(self):
        async def inner():
            await asyncio.sleep(2)
            return 'Works'

        return asyncio.run(inner())
    
    async def can_use_gather(self):
        asyncio.gather()

    async def create_hanger(self):
        hanger = Hanger()
        hanger.task = asyncio.create_task(hanger.start_async_process())
        return hanger
    
    async def stop_task_from_hanger(self, hanger):
        hanger.task.cancel()
