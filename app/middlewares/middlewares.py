from sanic import response
from sanic.log import logger
from sanic.exceptions import BadRequest


# exception handler for NotFound
async def wrong_url(request, exception):
    raise BadRequest("Oops, please enter a valid url")


# exception handler for SanicException
async def handle_sanic_exception(request, exception):
    return response.json({"error": str(exception), "status-code": exception.status_code}, status=exception.status_code,
                         headers={"Content-Type": "application/json"})


# Client checking middleware
async def client_checking_middleware(request):
    client = request.headers['user-agent']
    if 'chrome' not in client.lower():
        return response.json({"error": "Access denied. Only chrome allowed."}, status=403,
                             headers={"Content-Type": "application/json"})


# Request logging middleware
async def log_request(request):
    logger.info(f"Incoming Request: {request.ip}, {request.method}, {request.url}")


# Response logging middleware
async def log_response(request, response):
    logger.info(f"Outgoing response: {response.status}, {request.method}, {request.url}")
