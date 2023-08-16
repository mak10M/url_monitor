from sanic import Blueprint
from .email import email
from .url_monitor import url_monitor

blueprint_group = Blueprint.group(
    email, url_monitor
)
