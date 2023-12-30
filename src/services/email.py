from datetime import datetime, timedelta
from pathlib import Path
from fastapi import HTTPException, status
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from jose import jwt, JWTError
from pydantic import EmailStr


conf = ConnectionConfig(
    MAIL_USERNAME="martin.volodya@meta.ua",
    MAIL_PASSWORD="Dzidzio1234",
    MAIL_FROM="martin.volodya@meta.ua",
    MAIL_PORT=465,
    MAIL_SERVER="smtp.meta.ua",
    MAIL_FROM_NAME="Volodymyr",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def get_email_from_token(token: str, secret_key: str, algorithm: str):
    try:
        payload = jwt.decode(token, secret_key, [algorithm])
        email = payload["sub"]
        return email
    except JWTError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Invalid token for email verification")


async def send_email(email: EmailStr, username: str, token: str, host: str):
    print(email, username, token, host)
    try:
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)
