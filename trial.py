import asyncio
import aiohttp
import csv
from datetime import datetime
import time
import pandas as pd
from pathlib import Path
from sanic import Sanic, response

# Default urls
DEFAULT_URLS = [
    "https://www.google.com",
    "https://www.facebook.com",
    "https://www.twitter.com",
    "https://www.instagram.com",
    "https://www.linkedin.com",
    "https://www.youtube.com",
    "https://www.reddit.com",
    "https://www.github.com",
    "https://www.example.com",
    "https://www.wikipedia.org"
]

# Default path for log files
DEFAULT_PATH = Path("/Users/amandeep.miriyala/Desktop/prac")

# Default timeperiod gap for making next set of get requests
DEFAULT_DURATION = 4

# Maximum time(in seconds) server can wait for the response after making a get request
timeout = 3

# Set the time interval for auto-refresh (in seconds)
refresh_interval_seconds = 5

task = None

# Hold the csv data in html
html_response = ""

# Hold the user request menu in html
lobby_response = '''
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            body {
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                height: 100vh;
                                margin: 0;
                            }

                            .table-container {
                                width: 80%; /* Adjust the width as needed */
                            }

                            table {
                                width: 100%;
                                border-collapse: collapse;
                            }

                            th, td {
                                border: 1px solid black;
                                padding: 8px;
                                text-align: left;
                            }

                            th {
                                background-color: #f2f2f2;
                            }
                        </style>
                    </head>
                    <body>

                        <div class="table-container">
                            <h1>Help page</h1>
                            <table>
                                <tr>
                                    <th colspan="2">0.0.0.0:8000(Refer the table for options)</th>
                                </tr>
                                <tr>
                                    <td>/default.</td>
                                    <td>Default values set to duration, path, urls</td>
                                </tr>
                                <tr>
                                    <td>/i/&lt;duration&gt;</td>
                                    <td>Specify the monitoring interval in seconds (/i/5 : for 5 seconds), path and urls set to default values</td>
                                </tr>
                                <tr>
                                    <td>/l/&lt;path&gt;</td>
                                    <td>Specify the directory path to store the CSV logs (/l//Users/amandeep/Desktop/prac), duration and urls set to default values</td>
                                </tr>
                                <tr>
                                    <td>/u?urls</td>
                                    <td>Specify the list of URLs for monitoring(/u/?key1=url1&amp;key2=url2....), duration and path set to default values</td>
                                </tr>
                                <tr>
                                    <td>/i/&lt;duration&gt;/l/&lt;path&gt;</td>
                                    <td>Specify monitoring interval and path for log file, urls set to default value</td>
                                </tr>
                                <tr>
                                    <td>/i/&lt;duration&gt;/u?urls</td>
                                    <td>Specify monitoring interval and urls, path set to default value</td>
                                </tr>
                                <tr>
                                    <td>/l/&lt;path&gt;/u?urls</td>
                                    <td>Specify path and urls, duration set to default value</td>
                                </tr>
                                <tr>
                                    <td>/i/&lt;duration&gt;/l/&lt;path&gt;/u?urls</td>
                                    <td>Specify duration, path and urls</td>
                                </tr>
                                <tr>
                                    <th colspan="2">default_duration = 5s, default_path = /Users/amandeep/Desktop/prac, default_urls = you will find them in response data</th>
                                </tr>
                            </table>
                        </div>
                    </body>
                    </html>
                    '''

app = Sanic("mini_project")


def initialize_response():
    global html_response
    html_response = ""


# url get request sender
async def get_request_sender(session, url):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_time = time.time()  # Record the start time
    try:
        async with session.get(url, ssl=True, timeout=timeout) as res:  # Make get requests
            if res.status != 200:
                raise Exception
            return url, t, "Available", 200, time.time() - start_time
    except Exception as e:
        return url, t, "Unavailable", 404, time.time() - start_time


# Invoke get_request_sender for set of urls periodically and populates the data into log.csv file
async def periodic_tasks_launcher(timeperiod, urls, path):
    tasks = []  # Initialize the list for
    csv_file = path / "log.csv"  # Set the path for csv file
    # start = time.time()
    it = 0  # Initialise 'it' used to keep track of current phase of get requests

    # Clear existing log file data
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["URL", "Start_time", "Availability_Status", "Response_status", "Response_Time(s)"])

    # Invoke get_request_maker function periodically
    while "True":
        it += 1
        # Create http session
        async with aiohttp.ClientSession() as session:
            for url in urls:
                task = asyncio.create_task(get_request_sender(session, url))
                tasks.append(task)

            # Launch all tasks at the same time
            results = await asyncio.gather(*tasks)
            tasks.clear()  # Clear the tasks list
            task.cancel()
            # logging the data into csv file
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["---phase---", f"---{it}---", "---of---", "---get---", "---requests---"])
                for url, start_time, availability, response_status, response_time in results:
                    writer.writerow([str(url), str(start_time), str(availability), str(response_status),
                                     str(round(response_time, 2))])

            # Read the CSV file into a pandas DataFrame
            df = pd.read_csv(csv_file)
            results.clear()
            # Convert the DataFrame to an HTML table
            html_table = df.to_html(index=False)

            global html_response
            # Set the html body and refresh parameter
            html_response = f"""
                                <!DOCTYPE html>
                                <html>
                                <head>
                                    <style>
                                        body {{
                                            height: 100vh;
                                            margin: 0;
                                            font-family: Arial, sans-serif;
                                            background-color: #f8f8f8;
                                            display: flex;
                                            justify-content: center;
                                            align-items: center;
                                        }}

                                        .table-container {{
                                            width: 80%;
                                            max-height: 80vh; /* Adjust the max-height to control scrolling */
                                            overflow-y: auto; /* Enable vertical scrolling */
                                        }}

                                        table {{
                                            width: 100%;
                                            border-collapse: collapse;
                                            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                                            border: 1px solid #ddd;
                                            background-color: #fff;
                                            text-align: center;
                                        }}

                                        th, td {{
                                            padding: 12px 16px;
                                        }}

                                        th {{
                                            background-color: #f2f2f2;
                                        }}

                                        tr:nth-child(even) {{
                                            background-color: #f2f2f2;
                                        }}

                                        tr:hover {{
                                            background-color: #f7f7f7;
                                        }}
                                    </style>
                                    <meta http-equiv="refresh" content="{refresh_interval_seconds}">
                                </head>
                                <body>
                                    <div class="table-container">
                                        <table>
                                            {html_table}
                                        </table>
                                    </div>
                                </body>
                                </html>
                            """

            # Wait for timeperiod seconds before making next set of get requests
            await asyncio.sleep(timeperiod)


# Invoke periodic_tasks_launcher and redirect to route real_time_status
@app.route("main")
async def main(request, timeperiod, urls, path):
    global task
    if task and not task.done():
        task.cancel()
    task = asyncio.ensure_future(periodic_tasks_launcher(timeperiod, urls, path))
    return response.redirect("/real_time_status")


# Display the data in html format at UI
@app.route('/real_time_status')
async def rts(request):
    return response.html(html_response)


@app.route('/')
def options(request):
    return response.html(lobby_response)


@app.route('/default')
async def task_d(request):
    return await main(request, DEFAULT_DURATION, DEFAULT_URLS, DEFAULT_PATH)


@app.route('/i/<duration>')
async def task_t(request, duration):
    initialize_response()
    return await main(request, int(duration), DEFAULT_URLS, DEFAULT_PATH)


@app.route('/l/<path:path>')
async def task_p(request, path):
    initialize_response()
    return await main(request, DEFAULT_DURATION, DEFAULT_URLS, Path(path))


@app.route('/i/<duration>/l/<path:path>')
async def task_d_p(request, duration, path):
    initialize_response()
    return await main(request, int(duration), DEFAULT_URLS, Path(path))


@app.route('/u')
async def task_url(request):
    initialize_response()
    args = request.args
    urls = []
    for i in range(1, len(args) + 1):
        urls.append(args.get(f'key{i}'))

    return await main(request, DEFAULT_DURATION, urls, DEFAULT_PATH)


@app.route('/i/<duration>/u')
async def task_d_url(request, duration):
    initialize_response()
    args = request.args
    urls = []
    for i in range(1, len(args) + 1):
        urls.append(args.get(f'key{i}'))

    return await main(request, int(duration), urls, DEFAULT_PATH)


@app.route('/l/<path:path>/u')
async def task_p_url(request, path):
    initialize_response()
    args = request.args
    urls = []
    for i in range(1, len(args) + 1):
        urls.append(args.get(f'key{i}'))

    return await main(request, DEFAULT_DURATION, urls, Path(path))


@app.route('/i/<duration>/l/<path:path>/u')
async def task_d_p_url(request, duration, path):
    initialize_response()
    args = request.args
    urls = []
    for i in range(1, len(args) + 1):
        urls.append(args.get(f'key{i}'))

    return await main(request, int(duration), urls, Path(path))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)


