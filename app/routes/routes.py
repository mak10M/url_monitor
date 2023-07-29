from sanic import response, Blueprint
from app.config.config import DEFAULT_URLS, DEFAULT_PATH, DEFAULT_DURATION, lobby_response, email_form, final_response
from app.controller.managers import Main
from app.utils.request_parser import RequestParser
from pathlib import Path
from app.utils.email_sender import UserEmail


url_monitor = Blueprint("mini_project")


@url_monitor.route('/')
async def user_url_options(request):
    return await response.file(lobby_response)


@url_monitor.route('/enter_email')
async def user_email_form(request):
    return await response.file(email_form)


@url_monitor.route('/user_email', methods=['POST'])
async def user_email_response(request):
    UserEmail(request).write_email_into_csv()
    return response.redirect('/')


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
    return await response.file(final_response)