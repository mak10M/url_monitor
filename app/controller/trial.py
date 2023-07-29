import os
from sanic import response
from sanic.exceptions import SanicException
from app.utils.tasks_launcher_helpers import PeriodicTasksLauncher
from service import app

task = None


# Validate user data and Invoke periodic_tasks_launcher, redirect to route real_time_status
class Main:
    def __init__(self, timeperiod, urls, path):
        self.timeperiod = timeperiod
        self.urls = urls
        self.path = path

    async def main(self):
        try:
            time_period = int(self.timeperiod)
        except ValueError:
            raise SanicException("Duration should be an integer, please try again", status_code=400)

        if not os.path.exists(self.path):
            raise SanicException("Please enter a valid log file path", status_code=400)

        global task
        if task and not task.done():
            task.cancel()

        task = app.add_task(
            PeriodicTasksLauncher._launch_tasks_periodically(abs(time_period), self.urls, self.path)
        )

        # Use app.ctx.defer() instead of asyncio.sleep(2)
        await app.ctx.defer(2)

        return response.redirect("/real_time_status")





