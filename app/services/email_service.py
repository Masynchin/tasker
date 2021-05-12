from email.message import EmailMessage

import aiosmtplib

import config


async def send_confirmation_email(to_mail, token):
    """Отправка сообщения с подтверждающим регистрацию токеном"""
    message = EmailMessage()
    message["To"] = to_mail
    message["From"] = config.CONFIRMATION_EMAIL_USERNAME
    message["Subject"] = "Подтверждение почты для Tasker"
    message.set_content(
        f"Введите данный токен для подтверждения вашей почты: {token}")

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        username=config.CONFIRMATION_EMAIL_USERNAME,
        password=config.CONFIRMATION_EMAIL_PASSWORD,
        port=465,
        use_tls=True,
    )
