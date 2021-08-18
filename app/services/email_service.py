"""Сервис для работы с электронными письмами."""

from email.mime.text import MIMEText

import aiosmtplib

from app import config


EMAIL_TEMPLATE = """
<head>
<style type="text/css">
button {{
    background-color: #0d6efd;
    border-color: #0d6efd;
    color: #fff;

    padding: 10px;

    font-size: 1.25em;
    font-family: sans-serif;
    text-decoration: none;

    cursor: pointer;
    border: 1px solid transparent;
    border-radius: .25rem;
}}
h1 {{
    color: #000;
    font-family: sans-serif;
    margin-bottom: .5rem;
}}
</style>
</head>

<body>
<h1>Нажмите на кнопку для завершения регистрации</h1>
<a href="{confirm_url}">
    <button type="button">Подтвердить регистрацию</button>
</a>
</body>
"""


async def send_confirmation_email(to_mail: str, confirm_url: str):
    """Отправка сообщения с подтверждающим регистрацию токеном."""
    html = EMAIL_TEMPLATE.format(confirm_url=confirm_url)
    message = MIMEText(html, "html")
    message["To"] = to_mail
    message["From"] = config.CONFIRMATION_EMAIL_USERNAME
    message["Subject"] = "Подтверждение почты для Tasker"

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        username=config.CONFIRMATION_EMAIL_USERNAME,
        password=config.CONFIRMATION_EMAIL_PASSWORD,
        port=465,
        use_tls=True,
    )
