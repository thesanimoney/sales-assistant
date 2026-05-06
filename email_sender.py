import os
import smtplib
import ssl
from pathlib import Path
from email.message import EmailMessage


def send_html_email(
    html_path: str | Path,
    to_email: str,
    subject: str,
) -> None:
    """
    Read an HTML file from disk and send it as the body of an email via Gmail SMTP.

    Required environment variables:
        GMAIL_USER:     The Gmail address sending the email
        GMAIL_APP_PASSWORD: A Gmail app password (not your account password)

    Args:
        html_path: Path to the local HTML file.
        to_email:  Recipient email address.
        subject:   Email subject line.

    Raises:
        FileNotFoundError: If the HTML file doesn't exist.
        RuntimeError:      If required env vars are missing.
        smtplib.SMTPException: On SMTP-level failures.
    """
    
    
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    if not smtp_user or not smtp_pass:
        raise RuntimeError(
            "Missing SMTP_USER or SMTP_PASS environment variables."
        )

    path = Path(html_path)
    if not path.is_file():
        raise FileNotFoundError(f"HTML file not found: {path}")
    html_content = path.read_text(encoding="utf-8")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    msg.set_content(
        "This email contains an HTML version. "
        "If you're seeing this, your email client is not rendering HTML."
    )
    
    msg.add_alternative(html_content, subtype="html")

    context = ssl.create_default_context()
    
    SMTP_HOST = os.environ.get("SMTP_HOST")
    SMTP_PORT = int(os.environ.get("SMTP_PORT")) 
    
    if SMTP_PORT == 465:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    else:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)