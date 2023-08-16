from pathlib import Path

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
DEFAULT_DURATION = 5

# Maximum time(in seconds) server can wait for the response after making a get request
timeout = 3

# Set the time interval for auto-refresh (in seconds)
refresh_interval_seconds = 5

lobby_response = "/Users/amandeep.miriyala/Desktop/prac/app/templates/lobby_response.html"

email_form = "/Users/amandeep.miriyala/Desktop/prac/app/templates/user_email_id.html"

final_response = "/Users/amandeep.miriyala/Desktop/prac/app/templates/final_response.html"

user_email = "/Users/amandeep.miriyala/Desktop/prac/app/user_emails.txt"

log_response = "/Users/amandeep.miriyala/Desktop/prac/app/templates/log_response.html"
