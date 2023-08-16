# URLMONITORING SYSTEM

In this project we periodically monitor the availability of set of urls and log their timestamp, availability, status code, response time

## Setup

Follow the below steps to set up the environment and execute the code:

1. Clone the git repository.
2. Cd into it.
3. Create virtual environment using the Pipfile.
4. Install the requirements from req.txt.
5. Run the server using python service.py.

```bash
git clone git@github.com:mak10M/url_monitor.git
cd urlmonitor
pipenv install
pipenv shell
pip install -r req.txt
sanic app.service --dev
