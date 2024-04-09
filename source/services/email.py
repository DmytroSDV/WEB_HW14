from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from source.services.auth import auth_service
from source.config.conf import config

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_USERNAME,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME="TODO Systems",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)



async def send_email(email: EmailStr, username: str, host: str):
    """
    The send_email function sends an email to the user with a link to verify their email address.
            The function takes in three arguments:
                -email: the user's email address, which is used as a unique identifier for them.
                -username: the username of the user, which is displayed in the body of the message.
                -host: this is used as part of constructing a URL that will be sent to users so they can verify their account.
    
    :param email: EmailStr: Specify the email address of the recipient
    :param username: str: Pass the username to the template
    :param host: str: Construct a url that will be sent to the user so they can verify their account
    :return: A coroutine object
    :doc-author: Trelent
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)

async def send_password_email(email: EmailStr, username: str, password,  host: str):
    """
    The send_password_email function sends an email to the user with a link to reset their password.
        The function takes in the following parameters:
            - email: EmailStr, which is a string that represents an email address.
            - username: str, which is a string that represents the username of the user who requested 
                their password be reset.
            - password: str, which is a string that represents the new randomly generated temporary 
                password for this user's account. This will be used as part of our JWT token verification process later on in this tutorial series when we implement our frontend
    
    :param email: EmailStr: Validate the email address
    :param username: str: Pass the username to the template
    :param password: Send the password to the user
    :param host: str: Pass the host of the website to be used in the email template
    :return: A coroutine object
    :doc-author: Trelent
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email, "password": password})
        message = MessageSchema(
            subject="Password reset form",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="password_form.html")
    except ConnectionErrors as err:
        print(err)