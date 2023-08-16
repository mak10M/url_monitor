import asyncio
import aiohttp
from datetime import datetime
import time
from app.config.config import timeout


class GetRequestSender:

    def __init__(self, session):
        self.session = session

    async def send_get_request(self, url):
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_time = time.time()  # Record the start time
        try:
            async with self.session.get(url, ssl=True, timeout=timeout) as res:
                if res.status in list(range(200, 300)):
                    return url, t, "Available", res.status, time.time() - start_time
                else:
                    return url, t, "Unavailable", res.status, time.time() - start_time
        except aiohttp.ClientConnectionError:
            return url, t, "Connection Error", 0, time.time() - start_time
        except asyncio.TimeoutError:
            return url, t, "Timeout Error", 0, time.time() - start_time
        except Exception as e:
            return url, t, "unhandled Exception", 0, time.time() - start_time
