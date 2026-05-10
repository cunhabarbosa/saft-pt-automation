from pathlib import Path
from .models import AppConfig


def send_email(config: AppConfig, attachments: list[Path]) -> None:
    smtp = config.smtp
    emails = config.emails

    print(f"SMTP host: {smtp.host}")
    print(f"Sending to: {emails.to}")
    print(f"Attachments: {attachments}")

    # TODO: Move your current email sending logic here