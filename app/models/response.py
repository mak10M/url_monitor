from pydantic import BaseModel, HttpUrl
from datetime import datetime


class Response(BaseModel):
    url: HttpUrl
    time_stamp: datetime
    availability: str
    response_status: int
    response_time: float
