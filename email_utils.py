import smtplib
from email.message import EmailMessage

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
FROM_EMAIL = "alessandro.salvetti86@gmail.com"
FROM_PASSWORD = "60Toffo60!"  # IMPORTANT: must be an App Password
TO_EMAIL = "alessandro.salvetti86@gmail.com"

def send_email(subject, body, attachment_path=None):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL
    msg.set_content(body)

    if attachment_path:
        with open(attachment_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="text",
                subtype="csv",
                filename="jobs.csv"
            )

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(FROM_EMAIL, FROM_PASSWORD)
        smtp.send_message(msg)
