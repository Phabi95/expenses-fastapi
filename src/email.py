from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
from pydantic import EmailStr

import os
from dotenv import load_dotenv

load_dotenv()




conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
)


async def send_reset_email(email_to: EmailStr, token: str):

    reset_url = f"http://localhost:8501/?token={token}"

    html = f"""
    <h3>Επαναφορά Κωδικού</h3>
    <p>Κάνε κλικ στο παρακάτω link για να αλλάξεις τον κωδικό σου:</p>
    <a href="{reset_url}">Αλλαγή Κωδικού</a>
    <p>Αν το link δεν δουλεύει, κάνε αντιγραφή και επικόλληση το παρακάτω στον browser σου:</p>
    <p>{reset_url}</p>
    """

    message = MessageSchema(
        subject="Επαναφορά Κωδικού",
        recipients=[email_to],
        body=html,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(message)
