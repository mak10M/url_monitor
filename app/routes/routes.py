from sanic import response, Blueprint
from pathlib import Path
from app.config.config import DEFAULT_URLS, DEFAULT_PATH, DEFAULT_DURATION
from app.controller.managers import main


url_monitor = Blueprint("mini_project")


# Display the data in html format at UI
@url_monitor.route('/real_time_status')
async def rts(request):
    return await response.file("/Users/amandeep.miriyala/Desktop/prac/app/templates/final_response.html")


@url_monitor.route('/')
async def options(request):
    return await response.file('/Users/amandeep.miriyala/Desktop/prac/app/templates/lobby_response.html')


@url_monitor.route('/default')
async def task_d(request):
    return await main(request, DEFAULT_DURATION, DEFAULT_URLS, DEFAULT_PATH)


@url_monitor.route('/i/<duration>')
async def task_t(request, duration):
    return await main(request, int(duration), DEFAULT_URLS, DEFAULT_PATH)


@url_monitor.route('/l/<path:path>')
async def task_p(request, path):
    return await main(request, DEFAULT_DURATION, DEFAULT_URLS, Path(path))


@url_monitor.route('/i/<duration>/l/<path:path>')
async def task_d_p(request, duration, path):
    return await main(request, int(duration), DEFAULT_URLS, Path(path))


@url_monitor.route('/u')
async def task_url(request):
    args = request.args
    urls = []
    for i in range(1, len(args)+1):
        urls.append(args.get(f'key{i}'))

    return await main(request, DEFAULT_DURATION, urls, DEFAULT_PATH)


@url_monitor.route('/i/<duration>/u')
async def task_d_url(request, duration):
    args = request.args
    urls = []
    for i in range(1, len(args)+1):
        urls.append(args.get(f'key{i}'))

    return await main(request, int(duration), urls, DEFAULT_PATH)


@url_monitor.route('/l/<path:path>/u')
async def task_p_url(request, path):
    args = request.args
    urls = []
    for i in range(1, len(args)+1):
        urls.append(args.get(f'key{i}'))

    return await main(request, DEFAULT_DURATION, urls, Path(path))


@url_monitor.route('/i/<duration>/l/<path:path>/u')
async def task_d_p_url(request, duration, path):
    args = request.args
    urls = []
    for i in range(1, len(args)+1):
        urls.append(args.get(f'key{i}'))

    return await main(request, int(duration), urls, Path(path))
