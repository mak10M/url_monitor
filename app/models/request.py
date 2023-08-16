from typing import Optional, List
from pydantic import BaseModel, validator, HttpUrl, Field
from app.config.config import DEFAULT_URLS, DEFAULT_PATH, DEFAULT_DURATION


class TranslatorRequest(BaseModel):
    duration: int = Field(default=DEFAULT_DURATION, gt=0, lt=11)
    urls: List[HttpUrl] = Field(default=DEFAULT_URLS)
    path: str = Field(default=DEFAULT_PATH)

