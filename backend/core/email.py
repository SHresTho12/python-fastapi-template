from email.message import EmailMessage
from aiosmtplib import SMTP

from config import logger
from config import get_settings
from core.enums import MailSendType
from core.security import encoding_token
from templates import verification_mail, reset_password_mail


async def send_email(email, type: int, **kwargs):
    if type == MailSendType.VERIFICATION.value:
        subject = "Verification Mail"
        token = encoding_token({
            "id": kwargs['id'],
            "type": MailSendType.VERIFICATION.value
        })
        body = verification_mail(token)
    elif type == MailSendType.PASSWORD_RESET.value:
        subject = "Password Reset"
        token = encoding_token({
            "id": kwargs['id'],
            "type": MailSendType.PASSWORD_RESET.value
        })
        body = reset_password_mail(token)
    else:
        logger.error("Don't Sent Email!")
        return


    # Email Send
    email_message = EmailMessage()
    email_message['subject'] = subject
    email_message['From'] = get_settings().email_user
    email_message['To'] = email
    email_message.add_alternative(body, subtype='html')
    try:
        async with SMTP(hostname="smtp.gmail.com", port=465, use_tls=True) as smtp:
            await smtp.login(get_settings().email_user, get_settings().email_user_password)
            await smtp.send_message(email_message)
            await smtp.quit()
        logger.debug("Successfully sent email!")
    except Exception as e:
        logger.error(f"Error sending email: {e}")
