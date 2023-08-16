from sanic import Sanic
from sanic.exceptions import NotFound, SanicException
from app.routes import blueprint_group
from app.middlewares.middlewares import wrong_url, handle_sanic_exception, client_checking_middleware, log_request, log_response
import redis.asyncio as redis
from sanic.log import logger

app = Sanic("mini_project")
app.blueprint(blueprint_group)


async def connect_redis():
    app.ctx.redis = None
    r = redis.Redis()
    try:
        await r.ping()
        print("Connected to Redis")
    except redis.ConnectionError as e:
        logger.error(e)
        logger.error("<<<<< Could not connect to Redis! Shutting Down! >>>>>")
        app.stop()
    else:
        app.ctx.redis = r
        logger.info(f'<<<<< Connected to Redis >>>>>')


@app.listener('before_server_start')
async def setup_redis(loop):
    await connect_redis()


@app.listener('after_server_stop')
async def close_redis(loop):
    r = app.ctx.redis
    if r:
        await r.close()


@app.on_request("request")
async def rate_limit_middleware(request):
    client_ip = request.ip
    limit = 10
    time_frame = 60

    key = f"rate_limit:{client_ip}".encode()

    request_count = await app.ctx.redis.get(key)
    if request_count is None:
        request_count = 0

    # Check if the client has exceeded the rate limit
    if int(request_count) >= limit:
        # logger.info(int(request_count))
        # await app.ctx.redis.expire(key, time_frame)
        raise SanicException("Too many requests, please try again later", status_code=429)

    # Increment the request count for the client and set the expiration time
    await app.ctx.redis.incr(key)
    await app.ctx.redis.expire(key, time_frame)

# Exception handlers
app.exception(NotFound)(wrong_url)
app.exception(SanicException)(handle_sanic_exception)

# Middlewares
app.middleware("request")(log_request)
app.middleware("response")(log_response)
app.register_middleware(client_checking_middleware, attach_to="request")

if __name__ == "__main__":
    app.run(port=8000, debug=True)
