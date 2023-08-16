from sanic import response, Blueprint
from app.config.config import DEFAULT_URLS, DEFAULT_PATH, DEFAULT_DURATION, lobby_response, final_response
from app.controller.managers import Main
from app.utils.request_parser import RequestParser
from pathlib import Path
from app.utils.tasks_launcher_helpers import PeriodicTasksLauncher

url_monitor = Blueprint("url_monitor")


@url_monitor.route('/')
async def user_url_options(request):
    return response.html(await PeriodicTasksLauncher.read_file(lobby_response), status=200, headers={"Content-Type": "text/html"})


@url_monitor.route('/default')
async def default_route(request):
    return await Main(DEFAULT_DURATION, DEFAULT_URLS, DEFAULT_PATH).main()


@url_monitor.route('/i/<duration>')
async def duration_specific_route(request, duration):
    return await Main(duration, DEFAULT_URLS, DEFAULT_PATH).main()


@url_monitor.route('/l/<path:path>')
async def path_specific_route(request, path):
    return await Main(DEFAULT_DURATION, DEFAULT_URLS, Path(path)).main()


@url_monitor.route('/i/<duration>/l/<path:path>')
async def duration_path_specific_route(request, duration, path):
    return await Main(duration, DEFAULT_URLS, Path(path)).main()


@url_monitor.route('/u')
async def custom_url_specific_route(request):
    parser = RequestParser(request)
    parser.parse_request()
    return await Main(DEFAULT_DURATION, parser.urls, DEFAULT_PATH).main()


@url_monitor.route('/i/<duration>/u')
async def duration_custom_url_specific_route(request, duration):
    parser = RequestParser(request)
    parser.parse_request()
    return await Main(duration, parser.urls, DEFAULT_PATH).main()


@url_monitor.route('/l/<path:path>/u')
async def path_custom_url_specific_route(request, path):
    parser = RequestParser(request)
    parser.parse_request()
    return await Main(DEFAULT_DURATION, parser.urls, Path(path)).main()


@url_monitor.route('/i/<duration>/l/<path:path>/u')
async def duration_path_custom_url_specific_route(request, duration, path):
    parser = RequestParser(request)
    parser.parse_request()
    return await Main(duration, parser.urls, Path(path)).main()


# Display the data in html format at UI
@url_monitor.route('/real_time_status')
async def url_availability_response(request):
    return response.html(await PeriodicTasksLauncher.read_file(final_response), status=200, headers={"Content-Type": "text/html"})
