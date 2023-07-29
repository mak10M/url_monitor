import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from app.config.config import user_email
load_dotenv()


class UserEmail:
    USEREMAILFILE = user_email

    def __init__(self, request):
        self.request = request

    def write_email_into_csv(self):
        data = self.request.json
        email = data.get('email')
        with open(UserEmail.USEREMAILFILE, 'w') as file:
            file.write(email)


class EmailSender:

    def __init__(self, email_id):
        self.email_id = email_id

    def send_email(self, subject, body):
        # Sender's email credentials (replace with your own)
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        # Create a MIMEText object with the email body
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = self.email_id
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Replace with your SMTP server address and port
        server.starttls()  # Enable TLS encryption

        # Log in to the SMTP server
        try:
            server.login(sender_email, sender_password)
            # Handle the authentication error here
        except smtplib.SMTPAuthenticationError as e:
            print(f"Authentication error: {e}")
            # Handle other SMTP-related errors here
        except smtplib.SMTPException as e:
            print(f"SMTP error: {e}")
        # Send the email
        server.sendmail(sender_email, self.email_id, msg.as_string())
        # Close the connection to the SMTP server
        server.quit()

