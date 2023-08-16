import os
import asyncio
from sanic import Sanic, response
from sanic.exceptions import SanicException
from app.utils.tasks_launcher_helpers import PeriodicTasksLauncher
task = None


# Validate user data and Invoke periodic_tasks_launcher, redirect to route real_time_status
class Main:
    def __init__(self, timeperiod, urls, path):
        self.timeperiod = timeperiod
        self.urls = urls
        self.path = path

    async def main(self):
        app = Sanic.get_app()
        try:
            time_period = int(self.timeperiod)
            if time_period < 1 or time_period > 10:
                raise SanicException("Duration should be between 1s and 10s, please try again", status_code=400)
        except ValueError:
            raise SanicException("Duration should be an integer, please try again", status_code=400)

        if not os.path.exists(self.path):
            raise SanicException("Please enter a valid log file path", status_code=400)

        global task
        if task and not task.done():
            task.cancel()

        task = app.add_task(
            PeriodicTasksLauncher.launch_tasks_periodically(abs(time_period), self.urls, self.path)
        )

        await asyncio.sleep(4)

        return response.redirect("/real_time_status")
