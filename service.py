from sanic import Sanic, response
from app.routes.routes import url_monitor
from sanic.exceptions import NotFound

app = Sanic("mini_project")
app.blueprint(url_monitor)


@app.exception(NotFound)
async def wrong_url(request, exception):
    return response.text("Please enter a correct url")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
