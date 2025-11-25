import os
import smtplib
from email.message import EmailMessage

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # SSL port

FROM_EMAIL = os.getenv("FROM_EMAIL")
FROM_PASSWORD = os.getenv("FROM_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

def send_email(subject, body, attachment_path=None):
    print("Email debug -- FROM_EMAIL:", FROM_EMAIL)
    print("Email debug -- TO_EMAIL:", TO_EMAIL)
    print("Email debug -- Subject:", subject)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL
    msg.set_content(body)

    if attachment_path:
        try:
            with open(attachment_path, "rb") as f:
                msg.add_attachment(
                    f.read(),
                    maintype="application",
                    subtype="octet-stream",
                    filename=os.path.basename(attachment_path)
                )
            print("Email debug -- Attached:", attachment_path)
        except Exception as e:
            print("Email debug -- Failed to attach:", e)

    try:
        print("Email debug -- Connecting to server...")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(FROM_EMAIL, FROM_PASSWORD)
            smtp.send_message(msg)
        print("Email debug -- Email sent successfully!")
    except Exception as e:
        print("Email debug -- FAILED:", e)
        raise
