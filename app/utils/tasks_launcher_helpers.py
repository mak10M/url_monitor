import csv
import asyncio
import aiohttp
from sanic import Sanic
from app.utils.get_request_sender import GetRequestSender
import pandas as pd
from app.config.config import refresh_interval_seconds, final_response, log_response, user_email
from app.utils.email_sender import EmailSender
import aiofiles


class PeriodicTasksLauncher:
    RESPONSE_TEMPLATE_PATH = final_response
    LOG_RESPONSE_PATH = log_response

    @classmethod
    async def launch_tasks_periodically(cls, timeperiod, urls, path):
        tasks = []  # Initialize the list for
        csv_file = path / "log.csv"  # Set the path for csv file
        it = 0  # Initialise 'it' used to keep track of current phase of get requests

        await cls._truncate_file(cls.RESPONSE_TEMPLATE_PATH)
        email_id = await cls._read_email(user_email)
        # create EmailSender object
        email = EmailSender(email_id)
        # Create a dictionary with URLs as keys and value 0 for each URL
        url_dict = {url: 0 for url in urls}
        await cls._clear_csvfile(csv_file)

        # Invoke get_request_maker function periodically
        while "True":
            it += 1
            # Create aiohttp session
            async with aiohttp.ClientSession() as session:
                # Launch all tasks at the same time
                results = await cls._create_tasks(session, urls, tasks)
                # Clear the tasks list
                tasks.clear()
                await cls._write_into_csv(csv_file, it, results, url_dict, email)
                # clear the results list
                results.clear()
                await cls._final_response(csv_file)
                # Wait for timeperiod seconds before making next set of get requests
                await asyncio.sleep(timeperiod)

    @classmethod
    async def _truncate_file(cls, file_path):
        # Open the file in write mode and truncate its contents to 0 bytes
        async with aiofiles.open(file_path, "w") as file:
            await file.truncate()

    @classmethod
    async def _read_email(cls, file_path):
        # Open the file in read mode and read the first line and remove newline character if present
        async with aiofiles.open(file_path, 'r') as file:
            return await file.read()

    @classmethod
    async def _clear_csvfile(cls, file_path):
        # Clear existing log file data
        async with aiofiles.open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            await writer.writerow(["URL", "Start_time", "Availability_Status", "Response_status", "Response_Time(s)"])

    @classmethod
    async def _create_tasks(cls, session, urls, tasks):
        app = Sanic.get_app()
        request = GetRequestSender(session)
        for url in urls:
            tasks.append(app.add_task(request.send_get_request(url)))
        # Launch all tasks at the same time
        return await asyncio.gather(*tasks)

    @classmethod
    async def _write_into_csv(cls, file_path, it, results, url_dict, email):
        # logging the data into csv file and sending email notification
        async with aiofiles.open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            await writer.writerow(["---phase---", f"---{it}---", "---of---", "---get---", "---requests---"])
            for url, start_time, availability, response_status, response_time in results:
                await writer.writerow([str(url), str(start_time), str(availability), str(response_status), str(round(response_time, 2))])
                if availability in ["Unavailable", "Connection Error", "Timeout Error", "unhandled Exception"]:
                    url_dict[url] += 1
                    if url_dict[url] == 5:
                        email.send_email("url unavailable notification",
                                         f"{url} is unavailable for 5 consecutive requests")
                        url_dict[url] = 0
                else:
                    url_dict[url] = 0

    @classmethod
    async def _final_response(cls, csv_file):
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_file)
        # Convert the DataFrame to an HTML table
        html_table = df.to_html(index=False)
        html_template = await cls.read_file(cls.LOG_RESPONSE_PATH)
        html_response = html_template.format(html_table=html_table, refresh_interval_seconds=refresh_interval_seconds)
        await cls.write_file(cls.RESPONSE_TEMPLATE_PATH, html_response)

    @classmethod
    async def read_file(cls, filepath):
        async with aiofiles.open(filepath, mode="r") as file:
            html_content = await file.read()
        return html_content

    @classmethod
    async def write_file(cls, filepath, html_response):
        async with aiofiles.open(filepath, mode="w") as file:
            await file.write(html_response)
