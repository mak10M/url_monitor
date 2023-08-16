from sanic import response, Blueprint
from app.utils.email_sender import UserEmail
from app.config.config import email_form

email = Blueprint("email")


@email.route('/enter_email')
async def user_email_form(request):
    return await response.file(email_form)


@email.route('/user_email', methods=['POST'])
async def user_email_response(request):
    UserEmail(request).write_email_into_csv()
    return response.redirect('/')

