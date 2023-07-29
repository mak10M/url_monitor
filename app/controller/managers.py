import asyncio
import os
from sanic import response
from app.utils.tasks_launcher_helpers import PeriodicTasksLauncher
task = None


# Validate user data and Invoke periodic_tasks_launcher, redirect to route real_time_status
class Main:
    def __init__(self, timeperiod, urls, path):
        self.timeperiod = timeperiod
        self.urls = urls
        self.path = path

    async def main(self):
        try:
            int(self.timeperiod)
            if not os.path.exists(self.path):
                return response.text("Please enter a valid log file path")
            global task
            if task and not task.done():
                task.cancel()
            task = asyncio.ensure_future(PeriodicTasksLauncher._launch_tasks_periodically(abs(int(self.timeperiod)), self.urls, self.path))
            await asyncio.sleep(2)
            return response.redirect("/real_time_status")
        except ValueError:
            return response.text("Duration should be an integer, please try again")




