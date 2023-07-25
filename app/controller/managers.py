import asyncio
import aiohttp
import csv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime
import time
import pandas as pd
from sanic import response
from app.config.config import timeout, refresh_interval_seconds

task = None


def send_email(email_id, subject, body):

    # Sender's email credentials (replace with your own)
    sender_email = 'amandeep.miriyala@1mg.com'
    sender_password = 'whzvelrgaqspxiix'

    # Create a MIMEText object with the email body
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email_id
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Connect to the SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)  # Replace with your SMTP server address and port
    server.starttls()  # Enable TLS encryption

    # Log in to the SMTP server
    try:
        server.login(sender_email, sender_password)
    except smtplib.SMTPAuthenticationError as e:
        print(f"Authentication error: {e}")
        # Handle the authentication error here
    except smtplib.SMTPException as e:
        print(f"SMTP error: {e}")
        # Handle other SMTP-related errors here
    # Send the email
    server.sendmail(sender_email, email_id, msg.as_string())

    # Close the connection to the SMTP server
    server.quit()


# url get request sender
async def get_request_sender(session, url):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_time = time.time()  # Record the start time
    try:
        async with session.get(url, ssl=True, timeout=timeout) as res:
            if res.status == 200:
                return url, t, "Available", res.status, time.time() - start_time
            else:
                return url, t, "Unavailable", res.status, time.time() - start_time
    except aiohttp.ClientConnectionError:
        return url, t, "Connection Error", 0, time.time() - start_time
    except asyncio.TimeoutError:
        return url, t, "Timeout Error", 0, time.time() - start_time
    except Exception as e:
        return url, t, "unhandled Exception", 0, time.time() - start_time


# Invoke get_request_sender for set of urls periodically and populates the data into log.csv file
async def periodic_tasks_launcher(timeperiod, urls, path):
    file_path = "/Users/amandeep.miriyala/Desktop/prac/app/templates/final_response.html"
    # Open the file in write mode and truncate its contents to 0 bytes
    with open(file_path, "w") as file:
        file.truncate()

    tasks = []  # Initialize the list for
    csv_file = path / "log.csv"  # Set the path for csv file
    it = 0  # Initialise 'it' used to keep track of current phase of get requests

    with open('/Users/amandeep.miriyala/Desktop/prac/app/user_emails.txt', 'r') as file:
        email_id = file.readline().strip()  # Read the first line and remove newline character if present

    # Create a dictionary with URLs as keys and value 0 for each URL
    url_dict = {url: 0 for url in urls}

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
                task1 = asyncio.create_task(get_request_sender(session, url))
                tasks.append(task1)

            # Launch all tasks at the same time
            results = await asyncio.gather(*tasks)
            # Clear the tasks list
            tasks.clear()
            task1.cancel()

            # logging the data into csv file and sending email notification
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["---phase---", f"---{it}---", "---of---", "---get---", "---requests---"])
                for url, start_time, availability, response_status, response_time in results:
                    writer.writerow([str(url), str(start_time), str(availability), str(response_status),
                                     str(round(response_time, 2))])
                    if availability in ["Unavailable", "Connection Error", "Timeout Error", "unhandled Exception"]:
                        url_dict[url] += 1
                        if url_dict[url] == 5:
                            send_email(email_id, "url unavailable notification", f"{url} is unavailable for 5 consecutive requests")
                            url_dict[url] = 0
                    else:
                        url_dict[url] = 0

            # Read the CSV file into a pandas DataFrame
            df = pd.read_csv(csv_file)
            results.clear()
            # Convert the DataFrame to an HTML table
            html_table = df.to_html(index=False)

            with open('/Users/amandeep.miriyala/Desktop/prac/app/templates/log_response.html', 'r') as file:
                html_template = file.read()

            html_response = html_template.format(html_table=html_table, refresh_interval_seconds=refresh_interval_seconds)

            file_path = "/Users/amandeep.miriyala/Desktop/prac/app/templates/final_response.html"
            with open(file_path, "w") as file:
                file.write(html_response)

            # Wait for timeperiod seconds before making next set of get requests
            await asyncio.sleep(timeperiod)


# Invoke periodic_tasks_launcher and redirect to route real_time_status
async def main(request, timeperiod, urls, path):
    global task
    if task and not task.done():
        task.cancel()
    task = asyncio.ensure_future(periodic_tasks_launcher(timeperiod, urls, path))
    return response.redirect("/real_time_status")


async def is_valid_path(duration, urls, user_input, request):
    if not os.path.exists(user_input):
        return response.text("Please enter a valid log file path")
    return await main(request, duration, urls, Path(user_input))


